import sys
import os
import json
import re
from datetime import datetime
from helpers.export_excel import export_to_excel
from helpers.export_csv import export_to_csv
from helpers.common import validate_links, format_date_for_filename, SCRAPFLY_KEY
from scrapfly import ScrapflyClient, ScrapeConfig

# Try to import instagrapi
try:
    from instagrapi import Client as InstagrapiClient
    from instagrapi.extractors import extract_media_v1
    INSTAGRAPI_AVAILABLE = True
except ImportError:
    INSTAGRAPI_AVAILABLE = False
    print("⚠️  Warning: instagrapi not installed. Install it with: pip install instagrapi")
    print("   Without it, you'll need Instagram credentials to scrape ALL comments.")

client = ScrapflyClient(key=SCRAPFLY_KEY)

def find_in_dict(obj, target_key):
    """Recursively search for a key in nested dict/list structure"""
    if isinstance(obj, dict):
        if target_key in obj:
            return obj[target_key]
        for value in obj.values():
            result = find_in_dict(value, target_key)
            if result is not None:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = find_in_dict(item, target_key)
            if result is not None:
                return result
    return None

def extract_media_data_from_html(html):
    """Extract Instagram media data from HTML"""
    script_pattern = r'<script[^>]*>(.*?)</script>'
    scripts = re.findall(script_pattern, html, re.DOTALL)

    for script in scripts:
        if 'xdt_api__v1__media__shortcode__web_info' in script and len(script) > 10000:
            try:
                data = json.loads(script)
                media_info = find_in_dict(data, 'xdt_api__v1__media__shortcode__web_info')
                if media_info and 'items' in media_info and media_info['items']:
                    return media_info['items'][0]
            except json.JSONDecodeError:
                continue

    return None

# Constant: fields that must be lists (used by normalize_lists fallback)
LIST_FIELDS_THAT_MUST_BE_LISTS = {
    "audio_filter_infos",
    "additional_audio_assets",
    "candidates",
    "in",
    "video_versions",
    "carousel_media",
    "clips_items",
    "usertags",
    "sponsor_tags",
    "clips_attribution_info",
}

def normalize_lists(obj, list_fields):
    """
    Recursively walk a dict/list structure and replace None -> [] only when the
    current dict key is present in list_fields.

    This mutates the passed object in-place and returns it for convenience.
    """
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            # If value is None and the key is expected to be a list, replace it.
            if v is None and k in list_fields:
                obj[k] = []
            # Always recurse into nested dicts/lists to normalize deeply nested structures
            if isinstance(obj[k], (dict, list)):
                normalize_lists(obj[k], list_fields)
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                normalize_lists(item, list_fields)
    return obj

def safe_media_info(cl, media_pk, username=None, password=None):
    """
    Robust media_info wrapper with better error handling:
    - Try cl.media_info_v1() directly first
    - On Pydantic error, fetch raw data, normalize, then extract
    - On 401, attempt re-login and retry
    """
    # Strategy 1: Try the standard V1 API call
    try:
        return cl.media_info_v1(media_pk)
    except Exception as v1_err:
        print(f"⚠️  V1 API failed: {str(v1_err)[:100]}")
        
        # Strategy 2: Fetch raw data, normalize it, then extract
        try:
            # Get the raw media data from Instagram's private API
            media_id = str(media_pk)
            result = cl.private_request(f"media/{media_id}/info/")
            
            if not result or "items" not in result or not result["items"]:
                raise ValueError("No media data in API response")
            
            raw_media = result["items"][0]
            
            # Normalize all list fields to prevent Pydantic validation errors
            normalize_lists(raw_media, LIST_FIELDS_THAT_MUST_BE_LISTS)
            
            # Extract using the public extractor function
            return extract_media_v1(raw_media)
            
        except Exception as normalize_err:
            print(f"⚠️  Normalized extraction failed: {str(normalize_err)[:100]}")
            
            # Strategy 3: Check if it's a 401 and try re-login
            status_code = getattr(getattr(normalize_err, "response", None), "status_code", None)
            
            if status_code == 401:
                uname = username or os.getenv("INSTAGRAM_USERNAME")
                pwd = password or os.getenv("INSTAGRAM_PASSWORD")
                
                if uname and pwd:
                    try:
                        print("🔄 Attempting re-login...")
                        cl.login(uname, pwd)
                        
                        # Retry after login
                        result = cl.private_request(f"media/{media_pk}/info/")
                        if result and "items" in result and result["items"]:
                            raw_media = result["items"][0]
                            normalize_lists(raw_media, LIST_FIELDS_THAT_MUST_BE_LISTS)
                            return extract_media_v1(raw_media)
                        
                    except Exception as login_err:
                        print(f"❌ Re-login attempt failed: {login_err}")
            
            # If all strategies fail, raise a comprehensive error
            raise RuntimeError(
                f"All media_info strategies failed.\n"
                f"V1 error: {str(v1_err)[:200]}\n"
                f"Normalize error: {str(normalize_err)[:200]}"
            ) from normalize_err


def patch_client_media_info(cl, username=None, password=None):
    """
    Patch the client's media_info_v1 method to use our safe version
    This prevents Pydantic validation errors throughout the entire client
    """
    # Store the original method in a place where safe_media_info can access it
    if not hasattr(cl, '_original_media_info_v1'):
        cl._original_media_info_v1 = cl.media_info_v1
    
    def patched_media_info_v1(media_pk):
        """Wrapper that uses safe_media_info with the original method"""
        try:
            return safe_media_info_patched(cl, media_pk, username, password)
        except Exception as e:
            # If our safe version fails, try the original as last resort
            print(f"⚠️  Patched version failed, trying original: {str(e)[:100]}")
            return cl._original_media_info_v1(media_pk)
    
    # Replace the method
    cl.media_info_v1 = patched_media_info_v1
    return cl


def safe_media_info_patched(cl, media_pk, username=None, password=None):
    """
    Version of safe_media_info that uses the original (unpached) method
    to avoid infinite recursion
    """
    # Use the original method if available, otherwise fall back to current
    original_method = getattr(cl, '_original_media_info_v1', cl.media_info_v1)
    
    # Strategy 1: Try the original V1 API call
    try:
        return original_method(media_pk)
    except Exception as v1_err:
        error_str = str(v1_err)
        print(f"⚠️  V1 API failed: {error_str[:100]}")
        
        # Check if it's a login error - handle it immediately
        if 'login_required' in error_str.lower() or 'loginrequired' in str(type(v1_err)).lower():
            print("🔄 Login required error detected - attempting re-login...")
            uname = username or os.getenv("INSTAGRAM_USERNAME")
            pwd = password or os.getenv("INSTAGRAM_PASSWORD")
            
            if uname and pwd:
                try:
                    import time
                    time.sleep(1)  # Small delay before re-login
                    cl.login(uname, pwd)
                    print("✅ Re-login successful, retrying request...")
                    
                    # Save the new session
                    try:
                        cl.dump_settings('instagram_session.json')
                    except:
                        pass
                    
                    # Retry with fresh session
                    return original_method(media_pk)
                    
                except Exception as login_err:
                    print(f"❌ Re-login failed: {str(login_err)[:100]}")
        
        # Strategy 2: Fetch raw data, normalize it, then extract
        try:
            # Get the raw media data from Instagram's private API
            media_id = str(media_pk)
            result = cl.private_request(f"media/{media_id}/info/")
            
            if not result or "items" not in result or not result["items"]:
                raise ValueError("No media data in API response")
            
            raw_media = result["items"][0]
            
            # Normalize all list fields to prevent Pydantic validation errors
            normalize_lists(raw_media, LIST_FIELDS_THAT_MUST_BE_LISTS)
            
            # Extract using the public extractor function
            return extract_media_v1(raw_media)
            
        except Exception as normalize_err:
            error_str2 = str(normalize_err)
            print(f"⚠️  Normalized extraction failed: {error_str2[:100]}")
            
            # Check for login error again in normalized extraction
            if 'login_required' in error_str2.lower() or 'loginrequired' in str(type(normalize_err)).lower():
                print("🔄 Login required in normalized extraction - re-login attempt...")
                uname = username or os.getenv("INSTAGRAM_USERNAME")
                pwd = password or os.getenv("INSTAGRAM_PASSWORD")
                
                if uname and pwd:
                    try:
                        import time
                        time.sleep(1)
                        cl.login(uname, pwd)
                        print("✅ Re-login successful after normalization failure")
                        
                        # Save the new session
                        try:
                            cl.dump_settings('instagram_session.json')
                        except:
                            pass
                        
                        # Final retry after re-login
                        result = cl.private_request(f"media/{media_pk}/info/")
                        if result and "items" in result and result["items"]:
                            raw_media = result["items"][0]
                            normalize_lists(raw_media, LIST_FIELDS_THAT_MUST_BE_LISTS)
                            return extract_media_v1(raw_media)
                        
                    except Exception as final_login_err:
                        print(f"❌ Final re-login failed: {str(final_login_err)[:100]}")
            
            # Strategy 3: Check if it's a 401/403 and try re-login (legacy handler)
            status_code = getattr(getattr(normalize_err, "response", None), "status_code", None)
            
            if status_code in [401, 403]:
                uname = username or os.getenv("INSTAGRAM_USERNAME")
                pwd = password or os.getenv("INSTAGRAM_PASSWORD")
                
                if uname and pwd:
                    try:
                        print("🔄 HTTP 401/403 detected - attempting re-login...")
                        import time
                        time.sleep(1)
                        cl.login(uname, pwd)
                        
                        # Retry after login
                        result = cl.private_request(f"media/{media_pk}/info/")
                        if result and "items" in result and result["items"]:
                            raw_media = result["items"][0]
                            normalize_lists(raw_media, LIST_FIELDS_THAT_MUST_BE_LISTS)
                            return extract_media_v1(raw_media)
                        
                    except Exception as login_err:
                        print(f"❌ Re-login attempt failed: {login_err}")
            
            # If all strategies fail, raise a comprehensive error
            raise RuntimeError(
                f"All media_info strategies failed.\n"
                f"V1 error: {str(v1_err)[:200]}\n"
                f"Normalize error: {str(normalize_err)[:200]}\n"
                f"Hint: Try deleting 'instagram_session.json' and running again with fresh credentials."
            ) from normalize_err


def scrape_with_instagrapi(url, username=None, password=None):
    """
    Scrape Instagram using instagrapi (requires login)
    This method gets ALL comments reliably
    """
    if not INSTAGRAPI_AVAILABLE:
        print("❌ Error: instagrapi not installed")
        return None

    print(f"\nScraping with instagrapi (authenticated method)...")

    # Extract shortcode
    shortcode_match = re.search(r'/(p|reel)/([A-Za-z0-9_-]+)', url)
    if not shortcode_match:
        print("Error: Invalid URL")
        return None

    shortcode = shortcode_match.group(2)

    # Initialize client
    cl = InstagrapiClient()
    cl.delay_range = [1, 3]

    # Login logic with session validation
    session_file = 'instagram_session.json'
    logged_in = False

    if not username or not password:
        print("❌ Error: Username and password required")
        return None

    # Try saved session first
    if os.path.exists(session_file):
        try:
            print("🔄 Loading saved session...")
            cl.load_settings(session_file)
            
            # Validate session by making a simple request
            try:
                cl.get_timeline_feed()  # Simple test request
                logged_in = True
                print("✅ Saved session is valid")
            except Exception as validation_err:
                print(f"⚠️  Saved session expired or invalid: {str(validation_err)[:50]}")
                # Session invalid, delete it and force fresh login
                if os.path.exists(session_file):
                    os.remove(session_file)
                    print("🗑️  Deleted invalid session file")
        except Exception as e:
            print(f"⚠️  Could not load session: {str(e)[:50]}")
            if os.path.exists(session_file):
                os.remove(session_file)

    # If not logged in with session, do fresh login
    if not logged_in:
        try:
            print("🔐 Performing fresh login...")
            cl.login(username, password)
            cl.dump_settings(session_file)
            logged_in = True
            print("✅ Fresh login successful!")
        except Exception as e:
            print(f"❌ Login failed: {e}")
            # Try one more time after small delay
            import time
            time.sleep(2)
            try:
                print("🔄 Retrying login...")
                cl.login(username, password)
                cl.dump_settings(session_file)
                logged_in = True
                print("✅ Login successful on retry!")
            except Exception as e2:
                print(f"❌ Login failed again: {e2}")
                return None

    if not logged_in:
        print("❌ Error: Could not establish valid session")
        return None

    # CRITICAL: Patch the client to use our safe media_info everywhere
    cl = patch_client_media_info(cl, username, password)
    print("🔧 Client patched with safe media_info")

    try:
        # Get media info
        media_pk = cl.media_pk_from_code(shortcode)
        print(f"📌 Media PK: {media_pk}")
        
        media_info = safe_media_info_patched(cl, media_pk, username, password)

        print(f"📊 Post has {media_info.comment_count} comments (according to platform)")

        # Fetch ALL comments with pagination
        print("💬 Fetching all comments...")
        total_to_fetch = media_info.comment_count

        # media_comments has an 'amount' parameter to specify how many to fetch
        # By default it only fetches 20, so we need to specify the full amount
        all_comments = cl.media_comments(media_pk, amount=total_to_fetch)

        print(f"✅ Fetched {len(all_comments)} comments!")

        # Parse comments
        comments = []
        for i, comment_obj in enumerate(all_comments, 1):
            # Safely get attributes that may not exist
            is_reply = bool(getattr(comment_obj, 'parent_comment_id', None) or getattr(comment_obj, 'replied_to_comment_id', None))
            
            comment_dict = {
                'Comment Number': i,
                'User @': f'@{comment_obj.user.username}',
                'User URL': f'https://instagram.com/{comment_obj.user.username}',
                'Comment': comment_obj.text,
                'Comment Likes': comment_obj.like_count,
                'Comment Time': comment_obj.created_at_utc.strftime('%Y-%m-%d %H:%M:%S') if comment_obj.created_at_utc else '',
                'Is 2nd Level Comment': is_reply
            }
            comments.append(comment_dict)

        # Prepare metadata
        user = media_info.user
        caption = media_info.caption_text or ''
        lvl1 = [c for c in comments if not c['Is 2nd Level Comment']]
        lvl2 = [c for c in comments if c['Is 2nd Level Comment']]

        metadata = {
            'Now': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Post URL': url,
            'Publisher Nickname': user.username,
            'Publisher @': f'@{user.username}',
            'Publisher URL': f'https://instagram.com/{user.username}',
            'Publish Time': media_info.taken_at.strftime('%Y-%m-%d %H:%M:%S') if media_info.taken_at else '',
            'Post Likes': media_info.like_count,
            'Post Shares': 0,
            'Description': caption,
            'Number of 1st level comments': len(lvl1),
            'Number of 2nd level comments': len(lvl2),
            'Total Comments (actual)': len(comments),
            'Total Comments (platform says)': media_info.comment_count,
            'Difference': media_info.comment_count - len(comments)
        }

        return metadata, comments

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def scrape_with_scrapfly_only(url):
    """
    Scrape Instagram using only Scrapfly (no login required)
    WARNING: This method can only get metadata, NOT all comments
    Instagram requires authentication to access comments
    """
    print(f"\nScraping with Scrapfly (no auth - limited data)...")

    shortcode_match = re.search(r'/(p|reel)/([A-Za-z0-9_-]+)', url)
    if not shortcode_match:
        print("Error: Invalid URL")
        return None

    shortcode = shortcode_match.group(2)

    try:
        result = client.scrape(ScrapeConfig(
            url=url,
            render_js=True,
            rendering_wait=3000,
            asp=True,
            country='US',
        ))

        html = result.content
        media_data = extract_media_data_from_html(html)

        if not media_data:
            print("Error: Could not extract media data")
            return None

        # Prepare metadata (NO COMMENTS - they require authentication)
        user = media_data.get('user', {})
        owner = media_data.get('owner', user)
        caption_data = media_data.get('caption', {})
        caption = caption_data.get('text', '') if caption_data else ''

        metadata = {
            'Now': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Post URL': url,
            'Publisher Nickname': owner.get('username', 'unknown'),
            'Publisher @': f"@{owner.get('username', 'unknown')}",
            'Publisher URL': f"https://instagram.com/{owner.get('username', '')}",
            'Publish Time': datetime.fromtimestamp(media_data.get('taken_at', 0)).strftime('%Y-%m-%d %H:%M:%S'),
            'Post Likes': media_data.get('like_count', 0),
            'Post Shares': 0,
            'Description': caption,
            'Number of 1st level comments': 0,
            'Number of 2nd level comments': 0,
            'Total Comments (actual)': 0,
            'Total Comments (platform says)': media_data.get('comment_count', 0),
            'Difference': media_data.get('comment_count', 0)
        }

        total_comments = metadata["Total Comments (platform says)"]
        print(f"Got metadata only. {total_comments} comments NOT scraped (requires Instagram login)")

        return metadata, []

    except Exception as e:
        print(f"Error: {e}")
        return None

def scrape_instagram_video(url, instagram_username=None, instagram_password=None):
    """
    Main scraping function with two modes:
    1. Authenticated (with Instagram credentials) - Gets ALL comments
    2. Unauthenticated (no credentials) - Gets only metadata, NO comments

    Returns: dict with post metadata and list of comments
    """

    print(f"\n{'='*60}")
    print(f"Scraping: {url}")
    print(f"{'='*60}")

    # Check if we have Instagram credentials
    if instagram_username and instagram_password:
        print("✅ Instagram credentials provided - will fetch ALL comments")
        result = scrape_with_instagrapi(url, instagram_username, instagram_password)
    else:
        print("⚠️  No Instagram credentials - can only get metadata (NO COMMENTS)")
        print("   To get all comments, provide Instagram username & password")
        result = scrape_with_scrapfly_only(url)

    if not result:
        return None

    metadata, comments = result

    # Combine into single dict for easier handling
    post_info = {
        **metadata,
        'comments': comments
    }

    return post_info

def main():
    print("="*70)
    print("INSTAGRAM COMMENT SCRAPER v2.1 (FIXED)")
    print("="*70)

    # Important limitation warning
    print("\n⚠️  IMPORTANT LIMITATIONS:")
    print("   - Instagram limits comment access to ~50-60% of total comments")
    print("   - This is a security measure by Instagram, not a bug")
    print("   - For example: Post with 175 comments → You'll get ~91 comments")
    print("   - Missing comments are filtered/hidden by Instagram (spam, blocked users, etc.)")
    print("   - NO scraper can bypass this limit without violating Instagram ToS\n")

    # Ask if user wants to provide Instagram credentials
    print("REQUIREMENTS:")
    print("To scrape comments, you MUST login with Instagram credentials.")
    print("Without credentials, you can only get post metadata (no comments).\n")

    use_auth = input("Do you have Instagram credentials to use? (y/n): ").lower().strip() == 'y'

    instagram_username = None
    instagram_password = None

    if use_auth:
        instagram_username = input("Instagram username: ").strip()
        instagram_password = input("Instagram password: ").strip()

        if not INSTAGRAPI_AVAILABLE:
            print("\n⚠️  Installing instagrapi...")
            import subprocess
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "instagrapi"])
                print("✅ instagrapi installed. Please restart the script.")
                return
            except:
                print("❌ Failed to install instagrapi. Please install manually: pip install instagrapi")
                return
    else:
        print("\n⚠️  Proceeding without authentication - will get limited data only")

    num_videos = int(input("\n¿Cuántos links quieres scrapear? (máx 10): "))
    links = [input(f"Link {i+1}: ") for i in range(num_videos)]
    validate_links(links, "instagram")

    export_format = input("Formato de salida (csv/xlsx): ").lower()

    all_data = []
    for link in links:
        data = scrape_instagram_video(link, instagram_username, instagram_password)
        if data:
            all_data.append(data)

    if not all_data:
        print("\n❌ No se pudo scrapear nada.")
        return

    # Export using the existing export functions
    date_str = format_date_for_filename()
    outdir = os.path.join("scrape", "instagram")
    os.makedirs(outdir, exist_ok=True)
    outfile = os.path.join(outdir, f"instagram_{date_str}.{export_format}")

    # Prepare data for export
    for post in all_data:
        # Extract comments from the post
        comments = post.pop('comments', [])

        # Create metadata dict
        metadata = {k: v for k, v in post.items() if k != 'comments'}

        if export_format == "xlsx":
            export_to_excel(metadata, comments, "instagram", f"instagram_{date_str}")
        else:
            export_to_csv(metadata, comments, "instagram", f"instagram_{date_str}")

    print(f"\n✅ Datos exportados en {outfile}")

if __name__ == "__main__":
    main()
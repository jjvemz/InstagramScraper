# 📸 Instagram Scraper

Un scraper automatizado de Instagram desarrollado en Python que permite extraer metadatos y comentarios de publicaciones utilizando la API de Scrapfly.

## 🚀 Inicio Rápido

```bash
# 1. Clonar y navegar
git clone https://github.com/tu-usuario/InstagramScraper.git
cd InstagramScraper

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar credenciales
cp .env.example .env
# Editar .env con tu API key de Scrapfly

# 4. Ejecutar
python src/scraper_instagram.py
```

## ✨ Características

- **Extracción de datos completa**: Obtiene metadatos de publicaciones, reels y videos de Instagram
- **Información del usuario**: Nombre, handle, URL del perfil y estadísticas
- **Datos de engagement**: Likes, shares, comentarios con información detallada
- **Exportación múltiple**: Soporta formatos CSV y Excel (XLSX)
- **Procesamiento por lotes**: Hasta 10 URLs por ejecución
- **Validación automática**: Verifica URLs de Instagram antes del procesamiento
- **Estructura organizada**: Archivos guardados con fecha y organizados por carpetas

## 🛠️ Requisitos

### Software necesario
- Python 3.7 o superior
- Cuenta activa en [Scrapfly](https://scrapfly.io/) con API key válida

### Dependencias
Las dependencias se instalan automáticamente desde `requirements.txt`:
- `requests` - Para realizar peticiones HTTP
- `scrapfly-sdk` - SDK oficial de Scrapfly
- `openpyxl` - Para generar archivos Excel
- `beautifulsoup4` - Para parsing HTML (uso futuro)
- `lxml` - Parser XML/HTML
- `python-dateutil` - Manejo de fechas
- `python-dotenv` - Para manejo de variables de entorno

## 📦 Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/InstagramScraper.git
   cd InstagramScraper
   ```

2. **Crear entorno virtual** (recomendado):
   ```bash
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate
   
   # En macOS/Linux  
   source venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar Variables de Entorno**:
   - Regístrate en [Scrapfly](https://scrapfly.io/) y obtén tu API key
   - **Copia el archivo de ejemplo**:
     ```bash
     # En Windows
     copy .env.example .env
     
     # En macOS/Linux
     cp .env.example .env
     ```
   - **Edita el archivo `.env`** con tus credenciales reales:
     ```bash
     SCRAPFLY_API_KEY=scp-live-tu-clave-real-aqui
     ```

## 🚀 Uso

### Método 1: Ejecutar directamente
```bash
python src/scraper_instagram.py
```

### Método 2: Script por lotes (Windows)
```bash
run_scraper.bat
```

### Flujo de trabajo:
1. **Cantidad de URLs**: Ingresa cuántos enlaces procesarás (máximo 10)
2. **URLs de Instagram**: Proporciona las URLs una por una
3. **Formato de salida**: Elige entre CSV o XLSX
4. **Procesamiento**: El scraper extraerá los datos automáticamente
5. **Resultados**: Los archivos se guardan en `scrape/instagram/`

## 📁 Estructura del Proyecto

```
InstagramScraper/
│
├── src/                           # Código fuente
│   ├── helpers/                   # Módulos auxiliares
│   │   ├── common.py             # Configuración y utilidades
│   │   ├── export_csv.py         # Exportador CSV
│   │   └── export_excel.py       # Exportador Excel
│   └── scraper_instagram.py      # Script principal
│
├── scrape/                        # Archivos exportados
│   └── instagram/                 # Datos de Instagram por fecha
│
├── .env                          # Variables de entorno (NO subir a Git)
├── .env.example                   # Plantilla de configuración (sí en Git)
├── .gitignore                     # Archivos excluidos de Git
├── requirements.txt               # Dependencias Python
├── run_scraper.bat               # Script ejecutor Windows
└── README.md                     # Esta documentación
```

## 📊 Datos Extraídos

### Metadatos de Publicación:
- `post_url`: URL de la publicación
- `publisher_nickname`: Nombre del usuario
- `publisher_handle`: Handle (@usuario)
- `publisher_url`: URL del perfil
- `publish_time`: Fecha y hora de publicación
- `post_likes`: Número de likes
- `post_shares`: Número de compartidos
- `description`: Descripción/caption de la publicación
- `total_comments_actual`: Comentarios extraídos
- `total_comments_platform`: Total según la plataforma

### Datos de Comentarios:
- `comment_number`: Número secuencial del comentario
- `nickname`: Nombre del usuario que comenta
- `user_handle`: Handle del usuario
- `user_url`: URL del perfil del usuario
- `comment_text`: Texto del comentario
- `time`: Fecha del comentario
- `likes`: Likes del comentario
- `profile_pic_url`: URL de foto de perfil
- `followers`: Número de seguidores
- `is_2nd_level`: Si es respuesta a otro comentario
- `user_replied_to`: Usuario al que responde
- `num_replies`: Número de respuestas

## ⚙️ Configuración

### Variables de Entorno
El proyecto usa archivos de configuración de entorno para manejar credenciales de forma segura:

#### Archivos de configuración:
- **`.env.example`**: Plantilla con valores de ejemplo (incluida en Git)  
- **`.env`**: Archivo real con tus credenciales (excluido de Git)

#### Configuración inicial:
```bash
# 1. Copia el archivo de ejemplo
cp .env.example .env

# 2. Edita .env con tus valores reales
SCRAPFLY_API_KEY=scp-live-tu-clave-real-aqui
```

**🔒 Seguridad**: El archivo `.env` con tus credenciales reales está automáticamente excluido del repositorio por `.gitignore`.

### Personalización de Extracción
El archivo `scraper_instagram.py` contiene la lógica de scraping. Puedes modificar:
- Selectores HTML para extraer datos específicos
- Campos de datos recolectados
- Lógica de procesamiento de comentarios

## 📄 Formatos de Exportación

### CSV
- Formato ligero y universal
- Compatible con Excel y herramientas de análisis
- Ideal para procesamiento de grandes volúmenes

### Excel (XLSX)
- Formato profesional con estilos
- Separación visual entre metadatos y comentarios
- Mejor para presentaciones y reportes

## 🚨 Consideraciones Importantes

### ⚖️ Legal y Ética
- **Respeta los términos de servicio de Instagram**
- **Usa de manera responsable y ética**
- **Respeta la privacidad de los usuarios**
- **No hagas scraping excesivo**
- **Considera obtener permisos cuando sea necesario**

### 🔧 Limitaciones Técnicas
- Instagram cambia frecuentemente su estructura
- Límite de 10 URLs por ejecución
- Requiere clave API activa de Scrapfly
- Algunos datos pueden requerir ajustes en el código

### 🔒 Seguridad
- **El archivo `.env` está automáticamente excluido del repositorio**
- Nunca hardcodees claves API en el código
- Mantén tu archivo `.env` seguro y privado
- Usa variables de entorno para todas las credenciales
- Revisa que `.env` esté en `.gitignore` antes de hacer commit

## 🛡️ Solución de Problemas

### Error: "Invalid API key" o "No se encontró SCRAPFLY_API_KEY"
- **Archivo `.env` no existe**: Copia `.env.example` a `.env` usando `cp .env.example .env`
- **Variable no configurada**: Edita `.env` y asegúrate de que `SCRAPFLY_API_KEY` tenga tu clave real
- **Clave inválida**: Verifica tu API key en el dashboard de Scrapfly
- **Sin créditos**: Confirma que tienes créditos disponibles en tu cuenta Scrapfly

### Error: "No se pudo scrapear nada"
- Verifica que las URLs sean públicas y válidas
- Revisa tu conexión a internet
- Confirma que las URLs contengan "instagram"

### Problemas de instalación
- Actualiza pip: `pip install --upgrade pip`
- Usa Python 3.7+
- Crea un entorno virtual limpio

## 📈 Desarrollo Futuro

### Mejoras Planeadas:
- [ ] Soporte para Stories de Instagram
- [ ] Extracción de hashtags y menciones
- [ ] Análisis de engagement automático
- [ ] Integración con bases de datos
- [ ] API REST para uso remoto
- [ ] Dashboard web con visualizaciones

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1. Haz fork del repositorio
2. Crea una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Pautas de Contribución:
- Sigue las convenciones de código existentes
- Agrega tests para nuevas funcionalidades
- Actualiza la documentación
- Respeta los términos de uso de las plataformas

## 📝 Licencia

Este proyecto es de código abierto bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

## ⚠️ Disclaimer

Este software está destinado únicamente para fines educativos y de investigación. Los usuarios son responsables de cumplir con:

- Términos de servicio de Instagram
- Leyes de privacidad y protección de datos
- Regulaciones locales sobre web scraping
- Políticas de uso ético de datos

El uso indebido de esta herramienta es responsabilidad exclusiva del usuario.

## 🆘 Soporte

Si encuentras problemas o tienes preguntas:

1. Revisa la sección de [Solución de Problemas](#-solución-de-problemas)
2. Busca en los [Issues](https://github.com/tu-usuario/InstagramScraper/issues) existentes
3. Crea un nuevo issue con:
   - Descripción detallada del problema
   - Pasos para reproducir el error
   - Información del sistema y versión de Python
   - Logs de error si están disponibles

---

**Desarrollado con ❤️ para la comunidad de análisis de datos**

*¿Te gusta este proyecto? ¡Dale una estrella ⭐ en GitHub!*
# 🎬 VideoGenerador

**Generador automático de videos con narración TTS y subtítulos sincronizados**

VideoGenerador es una herramienta Python que transforma texto e imágenes en videos profesionales de formato vertical (ideal para redes sociales como Instagram Reels, TikTok y YouTube Shorts), con narración de voz automática y subtítulos dinámicos.

---

## ✨ Características

- 🎙️ **Narración automática** con síntesis de voz (Google TTS)
- 📝 **Subtítulos sincronizados** con bordes para máxima legibilidad
- 🎨 **Transiciones inteligentes** basadas en análisis de similitud
- 🎬 **Efecto Ken Burns** (zoom suave) en imágenes
- 🎵 **Soporte para música de fondo** opcional
- 📱 **Formato vertical optimizado** (1080x1920) para redes sociales
- ⚙️ **Altamente configurable** con múltiples parámetros ajustables

---

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/JhonyAdr/VideoGenerador.git
cd VideoGenerador
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Instalar FFmpeg
El proyecto requiere FFmpeg instalado en tu sistema.

**Windows:**
```bash
# Descarga desde: https://ffmpeg.org/download.html
# O usando chocolatey:
choco install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

---

## 📦 Requisitos

- Python 3.7 o superior
- FFmpeg instalado en el sistema
- Conexión a internet (para generación de audio TTS)
- Espacio en disco para archivos temporales

---

## 🎯 Uso Rápido

### 1. Preparar archivos de entrada

**Crear guion de texto** (`guion.txt`):
```txt
Bienvenidos a mi canal de videos educativos.
Hoy aprenderemos sobre inteligencia artificial.
La IA está transformando el mundo que conocemos.
```

**Agregar imágenes** en la carpeta `images/`:
```
images/
  ├── imagen1.jpg
  ├── imagen2.jpg
  └── imagen3.png
```

### 2. Ejecutar el generador
```bash
python gen.py
```

### 3. Obtener el video
El video final se generará en:
```
output_videos/video_final.mp4
```

---

## 📁 Estructura del Proyecto

```
VideoGenerador/
├── gen.py                 # Script principal
├── test.py                # Verificación de instalación
├── guion.txt              # Texto a narrar
├── requirements.txt       # Dependencias Python
├── README.md              # Este archivo
├── INFORME.md             # Documentación técnica detallada
│
├── images/                # 📁 Imágenes de entrada
│   └── (tus imágenes aquí)
│
├── audio/                 # 📁 Audio opcional
│   └── musica_fondo.mp3   # (opcional)
│
├── output_videos/         # 📁 Videos generados
│   └── video_final.mp4
│
├── tmp/                   # 📁 Archivos temporales de audio
│   └── narracion.mp3
│
└── tmp_images/            # 📁 Imágenes procesadas
    └── (archivos temporales)
```

---

## ⚙️ Configuración

Puedes modificar los parámetros en `gen.py`:

### Configuración de Video
```python
VIDEO_WIDTH = 1080          # Ancho en píxeles
VIDEO_HEIGHT = 1920         # Alto en píxeles (formato vertical)
FPS = 30                    # Cuadros por segundo
```

### Efectos y Transiciones
```python
CROSSFADE_DURATION = 0.4    # Duración de fundidos (segundos)
KEN_BURNS_SCALE = 1.08      # Factor de zoom (1.0 - 1.2)
BLACK_GAP = 0.3             # Duración de cortes negros
```

### Audio
```python
USE_TTS = True              # Usar síntesis de voz
TTS_LANG = "es"             # Idioma (es, en, fr, etc.)
MUSIC_VOL = 0.15            # Volumen de música (0.0 - 1.0)
NARR_VOL = 1.0              # Volumen de narración
```

### Subtítulos
```python
SUBTITLE_FONTSIZE = 72      # Tamaño de fuente
SUBTITLE_MAX_CHARS = 35     # Caracteres por línea
SUBTITLE_STROKE_WIDTH = 4   # Grosor del borde
```

---

## 🎨 Características Avanzadas

### 🔀 Transiciones Inteligentes
El sistema analiza automáticamente la similitud entre imágenes consecutivas y aplica:
- **Interpolación suave**: Para imágenes muy similares
- **Crossfade**: Para similitud media
- **Corte con gap negro**: Para imágenes muy diferentes

### 📐 Efecto Ken Burns
Zoom suave y gradual en imágenes estáticas para crear dinamismo visual.

### 🎵 Música de Fondo
Agrega un archivo de audio en `audio/` con uno de estos nombres:
- `musica_fondo.mp3`
- `musica_fondo.wav`
- `musica.mp3`

El sistema lo detectará y mezclará automáticamente con la narración.

### 📝 Subtítulos Profesionales
- Texto blanco con borde negro de 4px
- Word wrapping automático
- Centrado y posicionamiento optimizado
- Sincronización basada en duración y palabras

---

## 🧪 Verificar Instalación

Para verificar que todas las dependencias están correctamente instaladas:

```bash
python test.py
```

Deberías ver:
```
✅ MoviePy está instalado y funcionando correctamente.
```

---

## 📝 Formatos Soportados

### Imágenes de Entrada
- JPEG / JPG
- PNG
- WEBP
- BMP

### Audio de Salida
- Narración: MP3 (generado por gTTS)
- Música de fondo: MP3, WAV

### Video de Salida
- Formato: MP4 (H.264)
- Resolución: 1080x1920 (9:16)
- Bitrate: 8000 kbps
- Audio: AAC estéreo

---

## 🔧 Solución de Problemas

### Error: "MoviePy no se instala correctamente"
**Solución:**
```bash
pip uninstall moviepy
pip install moviepy==1.0.3
```

### Error: "FFmpeg not found"
**Solución:**
- Instala FFmpeg siguiendo las instrucciones de instalación
- Verifica con: `ffmpeg -version`

### Error: "No se encuentra la fuente"
**Solución:**
El sistema tiene fallback automático, pero para mejor calidad:
- **Windows**: Asegúrate de tener Arial instalado
- **Linux**: Instala `sudo apt install fonts-dejavu-core`
- **macOS**: Las fuentes del sistema funcionan automáticamente

### Calidad de audio TTS baja
**Solución:**
- Considera usar audio pregrabado profesional
- Coloca tu archivo en `audio/narracion.mp3`
- Cambia `USE_TTS = False` en `gen.py`

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Video educativo simple
```bash
# 1. Crea guion.txt con tu contenido educativo
# 2. Agrega 3-5 imágenes ilustrativas en images/
# 3. Ejecuta:
python gen.py
```

### Ejemplo 2: Con música de fondo
```bash
# 1. Agrega musica_fondo.mp3 en la carpeta audio/
# 2. Ajusta MUSIC_VOL en gen.py (ej: 0.20 para 20%)
# 3. Ejecuta:
python gen.py
```

### Ejemplo 3: Video largo con múltiples imágenes
```bash
# 1. Escribe un guion extenso en guion.txt
# 2. Agrega 10-20 imágenes en images/
# 3. El sistema dividirá automáticamente el texto
python gen.py
```

---

## 🎓 Casos de Uso

- 📚 **Contenido educativo** para YouTube/Instagram
- 📱 **Marketing en redes sociales** con narración automática
- 🎨 **Presentaciones multimedia** dinámicas
- 📖 **Storytelling visual** automatizado
- 🎬 **Prototipos de videos** rápidos y profesionales

---

## 🛠️ Pipeline de Procesamiento

1. **Lectura de guion** → Carga el texto desde `guion.txt`
2. **Búsqueda de imágenes** → Escanea carpeta `images/`
3. **Procesamiento de imágenes** → Ajusta a 1080x1920 con padding
4. **División de texto** → Fragmentos sincronizados con imágenes
5. **Generación de audio** → Síntesis TTS en español
6. **Análisis de transiciones** → Calcula similitud entre imágenes
7. **Cálculo de timings** → Sincroniza subtítulos con audio
8. **Renderizado final** → Exporta video MP4 HD

---

## 📊 Rendimiento

- **Procesamiento**: ~0.5-1 segundo por imagen
- **Generación TTS**: ~2-5 segundos
- **Renderizado**: Variable (depende de duración)
- **Uso de CPU**: Alto durante exportación (4 threads)
- **Uso de RAM**: ~500MB - 2GB según cantidad de imágenes

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---
 
## 🎉 Créditos

Desarrollado con:
- [MoviePy](https://zulko.github.io/moviepy/) - Edición de video
- [gTTS](https://gtts.readthedocs.io/) - Síntesis de voz
- [Pillow](https://python-pillow.org/) - Procesamiento de imágenes
- [scikit-image](https://scikit-image.org/) - Análisis de imágenes

---

 
**¡Disfruta creando videos automáticamente! 🎬✨**

---

*Última actualización: Octubre 2025*


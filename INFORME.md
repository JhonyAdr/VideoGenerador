# INFORME TÉCNICO VIDEOGENERADOR

## 1. INFORMACIÓN GENERAL

### 1.1 Descripción del Proyecto
**VideoGenerador** es un sistema automatizado de generación de videos desarrollado en Python que transforma texto e imágenes en videos profesionales con narración de voz sintética y subtítulos dinámicos. El proyecto está diseñado para crear contenido multimedia de formato vertical (1080x1920), ideal para plataformas como Instagram Reels, TikTok, YouTube Shorts y otras redes sociales.

### 1.2 Fecha de Análisis
28 de Octubre de 2025
 
---

## 2. ARQUITECTURA Y ESTRUCTURA DEL PROYECTO

### 2.1 Estructura de Directorios
```
VideoGenerador/
├── gen.py                    # Script principal de generación
├── test.py                   # Script de validación de dependencias
├── guion.txt                 # Archivo de entrada con el texto a narrar
├── images/                   # Directorio de imágenes de entrada
│   └── 1.jpeg
├── audio/                    # Directorio opcional para audio pregrabado
├── output_videos/            # Videos generados
│   └── video_final.mp4
├── tmp/                      # Archivos temporales de audio
│   └── narracion.mp3
└── tmp_images/               # Imágenes procesadas temporalmente
    ├── pad_000_1.jpeg
    └── text_*.png
```

### 2.2 Componentes Principales

#### 2.2.1 Módulo Principal (gen.py)
Archivo de 424 líneas que contiene toda la lógica de generación del video.

**Componentes clave:**
- **Sistema de configuración**: Variables globales para control de parámetros
- **Procesamiento de imágenes**: Redimensionamiento y ajuste
- **Generación de audio**: Síntesis de voz con gTTS
- **Sistema de subtítulos**: Generación y sincronización automática
- **Motor de transiciones**: Análisis de similitud entre imágenes
- **Pipeline de renderizado**: Construcción y exportación del video

#### 2.2.2 Módulo de Prueba (test.py)
Script de 10 líneas para verificar la correcta instalación de MoviePy.

---

## 3. ANÁLISIS TÉCNICO DETALLADO

### 3.1 Dependencias y Tecnologías

#### 3.1.1 Bibliotecas Core
- **moviepy (1.0.3)**: Motor principal de edición de video
- **Pillow**: Procesamiento y manipulación de imágenes
- **numpy**: Operaciones numéricas y matrices
- **gTTS (Google Text-to-Speech)**: Generación de narración de voz

#### 3.1.2 Bibliotecas de Análisis
- **scikit-image**: Cálculo de similitud estructural (SSIM)
- **imagehash**: Comparación perceptual de imágenes

#### 3.1.3 Compatibilidad
El proyecto incluye un parche de compatibilidad para diferentes versiones de Pillow:
```python
try:
    Image.ANTIALIAS = Image.Resampling.LANCZOS
except AttributeError:
    Image.ANTIALIAS = Image.LANCZOS
```

### 3.2 Configuración del Sistema

#### Parámetros de Video
| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| VIDEO_WIDTH | 1080 | Ancho del video en píxeles |
| VIDEO_HEIGHT | 1920 | Alto del video (formato vertical) |
| FPS | 30 | Cuadros por segundo |
| CODEC | libx264 | Códec de video H.264 |
| BITRATE | 8000k | Tasa de bits para calidad HD |

#### Parámetros de Efectos
| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| CROSSFADE_DURATION | 0.4s | Duración de transiciones cruzadas |
| KEN_BURNS_SCALE | 1.08 | Factor de zoom del efecto Ken Burns |
| BLACK_GAP | 0.3s | Duración de cortes negros |
| MUSIC_VOL | 0.15 | Volumen de música de fondo (15%) |
| NARR_VOL | 1.0 | Volumen de narración (100%) |

#### Parámetros de Subtítulos
| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| SUBTITLE_FONTSIZE | 72 | Tamaño de fuente |
| SUBTITLE_BOTTOM_MARGIN | 150px | Margen inferior |
| SUBTITLE_STROKE_WIDTH | 4px | Grosor del borde |
| SUBTITLE_MAX_CHARS | 35 | Caracteres máximos por línea |

#### Umbrales de Análisis
| Parámetro | Valor | Propósito |
|-----------|-------|-----------|
| SSIM_THRESH_INTERP | 0.62 | Umbral de similitud estructural |
| HASH_THRESH_CUT | 12 | Umbral de diferencia de hash |

### 3.3 Algoritmos y Funcionalidades

#### 3.3.1 Procesamiento de Imágenes

**Función: `pad_and_fit_images()`**
- **Propósito**: Ajustar imágenes al tamaño del video sin distorsión
- **Algoritmo**:
  1. Calcular ratio de aspecto óptimo
  2. Redimensionar manteniendo proporciones
  3. Agregar padding negro para completar el frame
  4. Guardar imagen procesada en directorio temporal

**Complejidad**: O(n) donde n = número de imágenes

#### 3.3.2 Análisis de Similitud

**Función: `pair_similarity_scores()`**
- **Métricas utilizadas**:
  - **SSIM (Structural Similarity Index)**: Mide similitud estructural
  - **Average Hash**: Compara hashes perceptuales
- **Retorna**: Diccionario con scores de similitud

**Función: `decide_transition()`**
- **Lógica de decisión**:
  ```
  SI ssim >= 0.62 Y hash <= 12:
      → interpolate (imágenes muy similares)
  SI NO, SI ssim >= 0.527:
      → crossfade (similitud media)
  SI NO:
      → cut_black (imágenes diferentes)
  ```

#### 3.3.3 Generación de Subtítulos

**Función: `make_text_image_with_stroke()`**
- Genera imágenes PNG transparentes con texto
- Aplica borde negro de 4px para legibilidad
- Texto blanco centrado con word wrapping automático
- Soporta múltiples líneas

**Función: `compute_subtitles_timing()`**
- Calcula timing basado en número de palabras
- Distribuye uniformemente sobre la duración del audio
- Sincroniza subtítulos con narración

#### 3.3.4 Efecto Ken Burns

**Función: `ken_burns_clip()`**
- Aplica zoom gradual del 100% al 108%
- Crea sensación de movimiento en imágenes estáticas
- Se activa automáticamente en transiciones con baja similitud

### 3.4 Pipeline de Generación (8 Fases)

#### Fase 1: Lectura del Guion
- Lee archivo `guion.txt`
- Validación de existencia
- Codificación UTF-8

#### Fase 2: Búsqueda de Imágenes
- Escanea directorio `images/`
- Soporta: JPG, JPEG, PNG, WEBP, BMP
- Ordenamiento alfabético

#### Fase 3: Procesamiento de Imágenes
- Ajuste a 1080x1920
- Padding proporcional
- Guardado en `tmp_images/`

#### Fase 4: División de Texto
- Divide guion en fragmentos
- Un fragmento por imagen
- Distribución equitativa de palabras

#### Fase 5: Generación de Audio
- Síntesis TTS con gTTS (idioma español)
- Generación de archivo MP3
- Guardado en `tmp/narracion.mp3`

#### Fase 6: Análisis de Transiciones
- Comparación de pares de imágenes consecutivas
- Decisión de tipo de transición
- Registro de acciones

#### Fase 7: Cálculo de Timings
- Sincronización de subtítulos
- Duración basada en palabras
- Ajuste a duración de audio

#### Fase 8: Renderizado Final
- Construcción de clips individuales
- Aplicación de subtítulos
- Inserción de transiciones
- Composición de audio (narración + música opcional)
- Exportación a MP4

---

## 4. FLUJO DE DATOS

```
guion.txt → [Lectura] → Texto
                              ↓
images/ → [Procesamiento] → Imágenes Ajustadas
                              ↓
Texto → [gTTS] → narracion.mp3
         ↓
[Análisis de Similitud] → Decisiones de Transición
         ↓
[División de Texto] → Fragmentos por Imagen
         ↓
[Cálculo de Timing] → Sincronización de Subtítulos
         ↓
[Generación de Clips] → Clips con Subtítulos
         ↓
[Aplicación de Transiciones] → Secuencia de Video
         ↓
[Composición de Audio] → Video + Narración + Música
         ↓
[Exportación] → output_videos/video_final.mp4
```

---

## 5. CARACTERÍSTICAS AVANZADAS

### 5.1 Sistema de Transiciones Inteligentes
- **Análisis automático** de similitud entre frames
- **Tres tipos de transiciones**:
  - Interpolación suave (imágenes similares)
  - Crossfade (similitud media)
  - Corte con gap negro (imágenes diferentes)

### 5.2 Subtítulos Profesionales
- Texto con borde negro (stroke)
- Centrado automático
- Word wrapping inteligente
- Sincronización precisa con audio

### 5.3 Audio Multi-capa
- **Narración principal**: Generada por TTS
- **Música de fondo opcional**: Volumen reducido (15%)
- **Mezcla automática**: CompositeAudioClip

### 5.4 Compatibilidad de Fuentes
Sistema de fallback para fuentes:
```python
FONT_OPTIONS = [
    "Arial-Bold.ttf",           # Windows/Mac
    "ArialBold.ttf",            # Linux
    "Helvetica-Bold.ttf",       # Mac
    "DejaVuSans-Bold.ttf",      # Linux
    "FreeSansBold.ttf",         # Linux
    "/System/Library/Fonts/...", # macOS absoluta
    "C:\\Windows\\Fonts\\..."    # Windows absoluta
]
```

---

## 6. RENDIMIENTO Y OPTIMIZACIÓN

### 6.1 Tiempos de Procesamiento
- **Procesamiento de imágenes**: ~0.5-1s por imagen
- **Generación TTS**: ~2-5s (depende de longitud)
- **Renderizado final**: Variable (depende de duración y resolución)

### 6.2 Uso de Recursos
- **CPU**: Alto durante renderizado (4 threads)
- **RAM**: Moderado (~500MB-2GB según cantidad de imágenes)
- **Disco**: Requiere espacio para archivos temporales

### 6.3 Optimizaciones Implementadas
- Uso de thumbnails (512x512) para análisis de similitud
- Almacenamiento en caché de imágenes procesadas
- Preset "medium" en x264 (balance velocidad/calidad)
- Procesamiento paralelo con 4 threads

---

## 7. FORMATO DE SALIDA

### 7.1 Especificaciones del Video
- **Resolución**: 1080x1920 (9:16)
- **FPS**: 30
- **Códec de video**: H.264 (libx264)
- **Códec de audio**: AAC
- **Bitrate**: 8000 kbps
- **Preset**: medium
- **Formato**: MP4

### 7.2 Calidad
- **Video**: HD (alta calidad)
- **Audio**: Estéreo AAC
- **Compresión**: Optimizada para streaming

---

## 8. MANEJO DE ERRORES Y VALIDACIONES

### 8.1 Validaciones de Entrada
- Existencia de `guion.txt`
- Presencia de imágenes en `images/`
- Validación de formatos de imagen
- Verificación de audio pregrabado (si USE_TTS=False)

### 8.2 Manejo de Excepciones
- Try-catch en cálculo de SSIM
- Fallback a fuente por defecto si no se encuentra TTF
- Manejo de errores en generación TTS
- Traceback completo en errores fatales

---

## 9. CASOS DE USO

### 9.1 Casos de Uso Principales
1. **Creación de contenido educativo**
   - Narración automática de lecciones
   - Visualización con imágenes ilustrativas

2. **Marketing en redes sociales**
   - Videos verticales para Instagram/TikTok
   - Subtítulos automáticos para mejor engagement

3. **Presentaciones multimedia**
   - Conversión de presentaciones estáticas a video
   - Narración automática de slides

4. **Documentación visual**
   - Tutoriales paso a paso
   - Explicaciones técnicas con imágenes

### 9.2 Escenarios de Ejemplo
**Entrada:**
- `guion.txt`: "Hola Mundo como estan"
- `images/1.jpeg`: Imagen de ejemplo

**Salida:**
- Video de ~3-5 segundos
- Narración en español
- Subtítulos sincronizados
- Formato vertical HD

---

## 10. LIMITACIONES Y CONSIDERACIONES

### 10.1 Limitaciones Técnicas
- **TTS**: Calidad de voz limitada a capacidades de gTTS
- **Idioma**: Configurado por defecto en español
- **Música de fondo**: Debe estar en directorio `audio/`
- **Fuentes**: Depende de fuentes instaladas en el sistema

### 10.2 Dependencias de Versión
- **MoviePy 1.0.3**: Versión específica requerida por compatibilidad
- **Pillow**: Requiere manejo de cambios en API entre versiones

### 10.3 Requisitos del Sistema
- Python 3.7+
- FFmpeg instalado en el sistema
- Espacio en disco para archivos temporales
- Conexión a internet para gTTS

---

## 11. CONCLUSIONES

### 11.1 Fortalezas del Proyecto
✅ **Automatización completa**: De texto a video sin intervención manual  
✅ **Transiciones inteligentes**: Análisis automático de similitud  
✅ **Subtítulos profesionales**: Con bordes y sincronización precisa  
✅ **Configuración flexible**: Múltiples parámetros ajustables  
✅ **Código bien estructurado**: Funciones modulares y reutilizables  
✅ **Compatibilidad multi-plataforma**: Windows, Linux, macOS  

### 11.2 Áreas de Mejora Potenciales
- Implementar progreso de renderizado en tiempo real
- Agregar soporte para múltiples idiomas de forma dinámica
- Sistema de plantillas de transiciones
- Interfaz gráfica (GUI)
- Soporte para videos de entrada (además de imágenes)
- Sistema de caché más robusto

### 11.3 Valoración Técnica
**Complejidad**: Media-Alta  
**Calidad del código**: Alta  
**Mantenibilidad**: Buena  
**Escalabilidad**: Media  
**Documentación interna**: Suficiente  

---

## 12. RECOMENDACIONES

### 12.1 Para Usuarios
1. Asegurarse de tener FFmpeg instalado
2. Usar MoviePy 1.0.3 específicamente
3. Mantener imágenes de resolución similar
4. Escribir guiones claros y concisos
5. Probar con pocas imágenes primero

### 12.2 Para Desarrolladores
1. Implementar logging más detallado
2. Agregar tests unitarios
3. Considerar usar argparse para CLI
4. Documentar funciones con docstrings
5. Implementar sistema de configuración JSON/YAML

---

## 13. ANEXOS

### 13.1 Comandos de Ejecución
```bash
# Ejecutar generación de video
python gen.py

# Verificar instalación de dependencias
python test.py
```

### 13.2 Ejemplo de guion.txt
```
Este es un ejemplo de guion para el generador de videos.
El texto será convertido automáticamente en narración.
Los subtítulos aparecerán sincronizados con el audio.
```

### 13.3 Formatos de Imagen Soportados
- JPEG / JPG
- PNG
- WEBP
- BMP

---

**Fin del Informe**

---

*Informe generado el 28 de octubre de 2025*  
*VideoGenerador v1.0*


import sys

print("🧩 Ejecutando desde:", sys.executable)

try:
    from moviepy.editor import VideoFileClip
    print("✅ MoviePy está instalado y funcionando correctamente.")
except Exception as e:
    print("❌ Error al importar moviepy:", e)

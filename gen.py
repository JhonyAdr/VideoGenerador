
import os
import math
import time
import hashlib
from typing import List, Dict, Tuple

from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont

 
from PIL import Image, ImageDraw, ImageFont

 
try:
    # Pillow >= 10 usa Image.Resampling.LANCZOS
    Image.ANTIALIAS = Image.Resampling.LANCZOS
except AttributeError:
    # Pillow < 10 todavía usa Image.LANCZOS
    Image.ANTIALIAS = Image.LANCZOS


import numpy as np
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips,
    ColorClip, CompositeAudioClip
)
from skimage.metrics import structural_similarity as ssim
import imagehash

# ------------------- CONFIG -------------------
IMAGES_DIR = "images"
AUDIO_DIR = "audio"
OUTPUT_DIR = "output_videos"
TMP_DIR = "tmp_images"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

GUION_FILE = "guion.txt"
USE_TTS = True
TTS_LANG = "es"
TTS_TMP = os.path.join("tmp", "narracion.mp3")
if not os.path.exists(os.path.dirname(TTS_TMP)):
    os.makedirs(os.path.dirname(TTS_TMP), exist_ok=True)

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_SIZE = (VIDEO_WIDTH, VIDEO_HEIGHT)

FPS = 30
CROSSFADE_DURATION = 0.4
KEN_BURNS_SCALE = 1.08
BLACK_GAP = 0.3
MUSIC_VOL = 0.15
NARR_VOL = 1.0

SSIM_THRESH_INTERP = 0.62
HASH_THRESH_CUT = 12

SUBTITLE_FONTSIZE = 72
SUBTITLE_BOTTOM_MARGIN = 150
SUBTITLE_STROKE_WIDTH = 4
SUBTITLE_MAX_CHARS = 35

FONT_OPTIONS = [
    "Arial-Bold.ttf",
    "ArialBold.ttf",
    "Helvetica-Bold.ttf",
    "DejaVuSans-Bold.ttf",
    "FreeSansBold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "C:\\Windows\\Fonts\\arialbd.ttf",
]



def read_guion() -> str:
    if os.path.exists(GUION_FILE):
        with open(GUION_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "No se encontró guion.txt. Por favor crea el archivo con tu texto."


def list_images(images_dir: str) -> List[str]:
    exts = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
    if not os.path.exists(images_dir):
        return []
    files = sorted([os.path.join(images_dir, f) for f in os.listdir(images_dir)
                    if f.lower().endswith(exts)])
    return files


def pad_and_fit_images(image_paths: List[str], target_wh: Tuple[int,int], out_dir: str = TMP_DIR) -> List[str]:
    os.makedirs(out_dir, exist_ok=True)
    w_t, h_t = target_wh
    result = []

    for i, p in enumerate(image_paths):
        print(f"  Procesando imagen {i+1}/{len(image_paths)}: {os.path.basename(p)}")
        im = Image.open(p).convert("RGB")
        w, h = im.size
        ratio = min(w_t / w, h_t / h)
        new_w, new_h = int(w * ratio), int(h * ratio)
        im_resized = im.resize((new_w, new_h), Image.LANCZOS)
        background = Image.new("RGB", (w_t, h_t), (0,0,0))
        x = (w_t - new_w)//2
        y = (h_t - new_h)//2
        background.paste(im_resized, (x,y))
        out_path = os.path.join(out_dir, f"pad_{i:03d}_{os.path.basename(p)}")
        background.save(out_path, quality=95)
        result.append(out_path)

    return result


def pair_similarity_scores(path_a: str, path_b: str, thumb=(512,512)) -> Dict[str, float]:
    a = Image.open(path_a).convert("RGB").resize(thumb)
    b = Image.open(path_b).convert("RGB").resize(thumb)
    A = np.asarray(a.convert("L"), dtype=float) / 255.0
    B = np.asarray(b.convert("L"), dtype=float) / 255.0
    try:
        s = ssim(A, B, data_range=1.0)
    except Exception:
        s = 0.0
    try:
        hdiff = imagehash.average_hash(a) - imagehash.average_hash(b)
        hdiff = int(abs(hdiff))
    except Exception:
        hdiff = 999
    return {"ssim": float(s), "hash": int(hdiff)}


def decide_transition(path_a: str, path_b: str) -> str:
    s = pair_similarity_scores(path_a, path_b)
    if s["ssim"] >= SSIM_THRESH_INTERP and s["hash"] <= HASH_THRESH_CUT:
        return "interpolate"
    if s["ssim"] >= (SSIM_THRESH_INTERP * 0.85):
        return "crossfade"
    return "cut_black"


def black_gap(duration: float, size: Tuple[int,int]):
    return ColorClip(size, color=(0,0,0), duration=duration)


def ken_burns_clip(image_path: str, duration: float, size: Tuple[int,int]):
    clip = ImageClip(image_path).set_duration(duration).resize(newsize=size)
    # resize with a time-based lambda para zoom suave
    return clip.resize(lambda t: 1 + (KEN_BURNS_SCALE - 1) * (t / max(1e-3, duration)))


def find_font():
    for font_path in FONT_OPTIONS:
        try:
            # si es una ruta absoluta y existe, usarla
            if os.path.isabs(font_path) and os.path.exists(font_path):
                ImageFont.truetype(font_path, SUBTITLE_FONTSIZE)
                print(f"[✓] Fuente encontrada: {font_path}")
                return font_path
            # intentar como nombre de fuente instalado (pil puede fallar pero lo intentamos)
            ImageFont.truetype(font_path, SUBTITLE_FONTSIZE)
            print(f"[✓] Fuente encontrada: {font_path}")
            return font_path
        except Exception:
            continue
    print("[!] No se encontró fuente TTF, usando fuente por defecto (calidad reducida)")
    return None


def make_text_image_with_stroke(text: str, width: int, height: int,
                                  fontsize: int = SUBTITLE_FONTSIZE,
                                  bottom_margin: int = SUBTITLE_BOTTOM_MARGIN,
                                  stroke_width: int = SUBTITLE_STROKE_WIDTH):
    img = Image.new("RGBA", (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    font_path = find_font()
    try:
        if font_path:
            font = ImageFont.truetype(font_path, fontsize)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    chars_per_line = SUBTITLE_MAX_CHARS
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if len(test) <= chars_per_line:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)

    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font)
        h_line = bbox[3] - bbox[1]
        line_heights.append(h_line)

    total_h = sum(line_heights) + (len(lines)-1) * 10
    y = height - bottom_margin - total_h

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0,0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x = (width - text_w) / 2
        for adj_x in range(-stroke_width, stroke_width+1):
            for adj_y in range(-stroke_width, stroke_width+1):
                draw.text((x+adj_x, y+adj_y), line, font=font, fill=(0,0,0,255))
        draw.text((x, y), line, font=font, fill=(255,255,255,255))
        y += line_heights[i] + 10

    return img


def make_text_png(text: str, size: Tuple[int,int]):
    w, h = size
    img = make_text_image_with_stroke(text, w, h)
    # usar sha1 para nombre estable y evitar colisiones raras en hash()
    key = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
    out = os.path.join(TMP_DIR, f"text_{key}.png")
    img.save(out)
    return out


def synthesize_tts_gtts(text: str, out_path: str = TTS_TMP, lang: str = TTS_LANG):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    print(f"[+] Generando narraci\u00f3n con TTS...")
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(out_path)
    print(f"[✓] Audio generado: {out_path}")
    return out_path


def compute_subtitles_timing(chunks: List[str], audio_path: str, max_duration: float = None):
    audio = AudioFileClip(audio_path)
    total_audio = audio.duration if max_duration is None else min(audio.duration, max_duration)
    counts = [len(c.split()) for c in chunks]
    total_words = sum(counts) if sum(counts)>0 else 1
    subs = []
    t = 0.0
    for cnt, txt in zip(counts, chunks):
        dur = max(0.8, (cnt/total_words) * total_audio)
        if t + dur > total_audio:
            dur = max(0.3, total_audio - t)
        subs.append({"text": txt, "start": t, "duration": dur})
        t += dur
    if t < total_audio and subs:
        subs[-1]["duration"] += (total_audio - t)
    audio.close()
    return subs


def split_text_by_images(text: str, num_images: int) -> List[str]:
    words = text.strip().split()
    if num_images <= 0:
        return [text]
    per = math.ceil(len(words) / num_images)
    chunks = []
    for i in range(0, len(words), per):
        chunks.append(" ".join(words[i:i+per]))
    while len(chunks) > num_images:
        a = chunks.pop()
        chunks[-1] = chunks[-1] + " " + a
    return chunks

# ------------------- MAIN PIPELINE -------------------

def build_video(clean_tmp: bool = False):
    print("\n" + "="*60)
    print("    VIDEO PIPELINE UNIVERSAL - INICIANDO")
    print("="*60 + "\n")
    start_time = time.time()

    print("[1/8] Leyendo guion...")
    guion = read_guion()
    if "No se encontr" in guion:
        print(f"[ERROR] {guion}")
        return None
    print(f"[✓] Guion cargado: {len(guion)} caracteres")

    print("\n[2/8] Buscando imágenes...")
    image_paths = list_images(IMAGES_DIR)
    if not image_paths:
        print(f"[ERROR] No se encontraron im\u00e1genes en '{IMAGES_DIR}/'")
        return None
    print(f"[✓] {len(image_paths)} im\u00e1genes encontradas")

    print(f"\n[3/8] Ajustando im\u00e1genes a {VIDEO_WIDTH}x{VIDEO_HEIGHT}...")
    padded = pad_and_fit_images(image_paths, VIDEO_SIZE, out_dir=TMP_DIR)

    print("\n[4/8] Dividiendo texto en fragmentos...")
    chunks = split_text_by_images(guion, len(padded))
    print(f"[✓] {len(chunks)} fragmentos de texto creados")

    print("\n[5/8] Procesando audio...")
    if USE_TTS:
        audio_path = synthesize_tts_gtts(guion, out_path=TTS_TMP)
    else:
        audio_path = os.path.join(AUDIO_DIR, "narracion.mp3")
        if not os.path.exists(audio_path):
            print(f"[ERROR] USE_TTS=False pero no se encontr\u00f3 '{audio_path}'")
            return None
        print(f"[✓] Audio cargado: {audio_path}")

    print("\n[6/8] Analizando transiciones...")
    decisions = []
    for i in range(len(padded)-1):
        a = padded[i]
        b = padded[i+1]
        action = decide_transition(a, b)
        decisions.append(action)
        print(f"  Imagen {i+1} -> {i+2}: {action}")

    print("\n[7/8] Calculando tiempos de subt\u00edtulos...")
    subtitles = compute_subtitles_timing(chunks, audio_path)

    print("\n[8/8] Construyendo video...")
    clips = []

    # crear clips con subtítulos y transiciones simples
    for i, img_path in enumerate(padded):
        if i < len(subtitles):
            dur = subtitles[i]["duration"]
            text = subtitles[i]["text"]
        else:
            narr = AudioFileClip(audio_path)
            dur = max(1.0, (narr.duration / max(1, len(padded))))
            narr.close()
            text = ""

        print(f"  Procesando clip {i+1}/{len(padded)} ({dur:.1f}s)")
        clip = ImageClip(img_path).set_duration(dur).resize(newsize=VIDEO_SIZE)

        if i > 0:
            prev = padded[i-1]
            sim = pair_similarity_scores(prev, img_path)
            if sim["ssim"] < SSIM_THRESH_INTERP or sim["hash"] > HASH_THRESH_CUT:
                clip = ken_burns_clip(img_path, dur, VIDEO_SIZE)

        if text.strip():
            txt_png = make_text_png(text, VIDEO_SIZE)
            txt_clip = ImageClip(txt_png, ismask=False).set_duration(dur)
            comp = CompositeVideoClip([clip, txt_clip], size=VIDEO_SIZE).set_duration(dur)
        else:
            comp = clip

        clips.append(comp)
        if i < len(padded)-1:
            action = decisions[i]
            if action == "cut_black":
                clips.append(black_gap(BLACK_GAP, VIDEO_SIZE))

    print("\n[+] Concatenando clips con transiciones...")
    # Usar concatenate sin padding negativo para compatibilidad
    final = concatenate_videoclips(clips, method="compose")

    print("[+] Añadiendo audio...")
    audio_narr = AudioFileClip(audio_path).volumex(NARR_VOL)

    music_path = None
    for cand in ["musica_fondo.mp3", "musica_fondo.wav", "musica.mp3"]:
        p = os.path.join(AUDIO_DIR, cand)
        if os.path.exists(p):
            music_path = p
            break

    if music_path:
        print(f"[✓] M\u00fasica de fondo detectada: {os.path.basename(music_path)}")
        music = AudioFileClip(music_path).volumex(MUSIC_VOL).set_duration(final.duration)
        combined_audio = CompositeAudioClip([music, audio_narr])
    else:
        print("[!] No se detectó m\u00fasica de fondo (opcional)")
        combined_audio = audio_narr

    final = final.set_audio(combined_audio)
    final = final.set_duration(min(final.duration, audio_narr.duration))

    output_path = os.path.join(OUTPUT_DIR, "video_final.mp4")
    print(f"\n[+] Exportando video a: {output_path}")
    final.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
        bitrate="8000k"
    )

    elapsed = time.time() - start_time
    print("\n" + "="*60)
    print(f"  ✓ VIDEO COMPLETADO EN {elapsed:.1f} SEGUNDOS")
    print(f"  📁 Archivo: {output_path}")
    print("="*60 + "\n")

    if clean_tmp:
        try:
            for f in os.listdir(TMP_DIR):
                os.remove(os.path.join(TMP_DIR, f))
        except Exception:
            pass

    return output_path


if __name__ == "__main__":
    try:
        result = build_video(clean_tmp=False)
        if result:
            print(f"\n✅ ¡Listo! Tu video est\u00e1 en: {result}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

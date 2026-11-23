"""Genera el video promocional de Eke con narración (Módulo 1.3 - SEO de video).

Crea escenas con las fotos de /assets-src (efecto de zoom, textos en pantalla),
narra cada escena con la voz en español de Windows (SAPI) y une todo con ffmpeg.

Salidas en src/static/video/:
  eke-enchiladas-de-huejutla.mp4   video H.264 + AAC (faststart, apto para web)
  eke-enchiladas-de-huejutla.vtt   subtítulos en español (accesibilidad y SEO)
y la miniatura src/static/img/video-poster-eke.webp

Requisitos: Windows (voz "Microsoft Helena" o "Sabina"), ffmpeg en el PATH y Pillow.
Uso:  python scripts/make_video.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets-src"
OUT_DIR = ROOT / "src" / "static" / "video"
NAME = "eke-enchiladas-de-huejutla"
W, H, FPS = 1280, 720, 24
WINE, CREAM, YELLOW, DARK = (96, 18, 18), (248, 235, 214), (254, 201, 61), (40, 14, 10)
FONTS = Path("C:/Windows/Fonts")

# (tipo, imagen, título, subtítulo, narración)
SCENES = [
    ("intro", None, "Comida Tradicional Huasteca", "Desde Huejutla, Hidalgo",
     "Bienvenidos a Eke, comida tradicional huasteca, desde Huejutla, Hidalgo."),
    ("full", "hero-enchiladas-de-huejutla", "Enchiladas de Huejutla", "Especialidad de la casa",
     "Nuestras enchiladas de Huejutla se preparan con salsa de chile seco tostado en comal, "
     "tortilla de maíz recién hecha, y queso fresco de la región."),
    ("card", "enchiladas-de-huejutla-orden-tradicional", "Orden tradicional", "5 piezas · $140 MXN",
     "La orden tradicional trae cinco piezas con queso, lechuga y cebolla."),
    ("card", "enchiladas-con-cecina-huasteca", "Enchiladas con cecina", "5 piezas · $170 MXN",
     "Y para un desayuno completo, pídelas con cecina de la Huasteca."),
    ("card", "paquete-familiar-eke-enchiladas", "Paquete Familiar Eke", "12 enchiladas · $360 MXN",
     "Para compartir en familia, tenemos el paquete familiar, con doce enchiladas, salsa extra y complementos."),
    ("card", "salsa-huasteca-eke-250-ml", "Salsa Huasteca Eke", "Envíos a todo México",
     "Además, llévate nuestra salsa huasteca en frasco. Hacemos envíos a todo México."),
    ("card", "desde-huejutla-hidalgo-catedral", "Desde Huejutla, Hidalgo", "El sabor de nuestra tierra",
     "Llevamos a tu mesa el sabor de nuestra tierra."),
    ("outro", None, "Ordena en línea", "Pago seguro · Entrega en Huejutla · Envíos nacionales",
     "Haz tu pedido en línea en la tienda de Eke. Enchiladas de Huejutla, hechas con pasión."),
]


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for candidate in (name, "segoeuib.ttf", "arialbd.ttf"):
        p = FONTS / candidate
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


F_TITLE = font("georgiab.ttf", 64)
F_SCRIPT = font("georgiaz.ttf", 70)
F_SUB = font("segoeuib.ttf", 34)
F_SMALL = font("segoeui.ttf", 28)


# ------------------------------------------------------------------ narración
def speak(text: str, wav: Path) -> float:
    ps = (
        "Add-Type -AssemblyName System.Speech;"
        "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
        "$v=$s.GetInstalledVoices()|Where-Object{$_.VoiceInfo.Culture.Name -like 'es-*'}|Select-Object -First 1;"
        "if($v){$s.SelectVoice($v.VoiceInfo.Name)};"
        "$s.Rate=-1;"
        f"$s.SetOutputToWaveFile('{wav}');"
        "$s.Speak([Console]::In.ReadToEnd());$s.Dispose()"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], input=text.encode("utf-8"), check=True)
    with wave.open(str(wav)) as w:
        return w.getnframes() / w.getframerate()


def join_audio(parts: list[tuple[Path, float]], out: Path, lead: float = 0.5) -> None:
    """Une las narraciones respetando la duración de cada escena (silencio entre ellas)."""
    with wave.open(str(parts[0][0])) as w0:
        params = w0.getparams()
    rate, width, ch = params.framerate, params.sampwidth, params.nchannels
    with wave.open(str(out), "wb") as o:
        o.setparams(params)
        for wav, scene_len in parts:
            with wave.open(str(wav)) as w:
                frames = w.readframes(w.getnframes())
            silence_lead = b"\x00" * int(rate * lead) * width * ch
            used = lead + len(frames) / (rate * width * ch)
            silence_tail = b"\x00" * int(rate * max(0.0, scene_len - used)) * width * ch
            o.writeframes(silence_lead + frames + silence_tail)


# ------------------------------------------------------------------ dibujo
def cover(img: Image.Image, w: int, h: int) -> Image.Image:
    s = max(w / img.width, h / img.height)
    r = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (r.width - w) // 2, (r.height - h) // 2
    return r.crop((x, y, x + w, y + h))


def textile_strip() -> Image.Image:
    t = Image.open(SRC / "textil-bordado-huasteco.png").convert("RGB")
    t = t.resize((round(t.width * 70 / t.height), 70), Image.LANCZOS)
    strip = Image.new("RGB", (W, 70))
    for x in range(0, W, t.width):
        strip.paste(t, (x, 0))
    return strip


TEXTILE = textile_strip()


def centered(d: ImageDraw.ImageDraw, y: int, text: str, f, fill) -> None:
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=fill)


def caption(frame: Image.Image, title: str, sub: str) -> None:
    band = Image.new("RGBA", (W, 150), (*WINE, 235))
    frame.paste(band, (0, H - 150), band)
    d = ImageDraw.Draw(frame)
    d.text((60, H - 135), title, font=F_TITLE, fill=(255, 248, 236))
    d.text((62, H - 58), sub, font=F_SUB, fill=YELLOW)


def brand_card(title: str, sub: str, outro: bool) -> Image.Image:
    base = Image.new("RGB", (W, H), CREAM)
    base.paste(TEXTILE, (0, H - 70))
    logo = Image.open(SRC / "logo-eke-comida-tradicional-huasteca.png").convert("RGBA")
    logo = logo.resize((logo.width * 2, logo.height * 2), Image.LANCZOS)
    base.paste(logo, ((W - logo.width) // 2, 90 if not outro else 60), logo)
    d = ImageDraw.Draw(base)
    if outro:
        btn_w, btn_h = 520, 96
        x0, y0 = (W - btn_w) // 2, 330
        d.rounded_rectangle((x0, y0 + 8, x0 + btn_w, y0 + btn_h + 8), 18, fill=(217, 165, 32))
        d.rounded_rectangle((x0, y0, x0 + btn_w, y0 + btn_h), 18, fill=YELLOW)
        centered(d, y0 + 14, title, F_TITLE, DARK)
        centered(d, 470, sub, F_SMALL, WINE)
        centered(d, 520, "Eke · Comida Tradicional Huasteca", F_SUB, DARK)
    else:
        centered(d, 330, title, F_SCRIPT, WINE)
        centered(d, 430, sub, F_SUB, DARK)
    return base


def scene_frames(kind: str, img_name: str | None, title: str, sub: str, seconds: float):
    n = max(1, round(seconds * FPS))
    if kind in ("intro", "outro"):
        card = brand_card(title, sub, kind == "outro")
        for i in range(n):
            z = 1 + 0.03 * i / n
            f = cover(card, round(W * z), round(H * z)).resize((W, H)) if z > 1 else card
            yield f, i, n
        return
    src = Image.open(SRC / f"{img_name}.png").convert("RGB")
    if kind == "full":
        big = cover(src, round(W * 1.15), round(H * 1.15))
        for i in range(n):
            t = i / max(1, n - 1)
            z = 1.0 + 0.12 * t                      # acercamiento progresivo
            cw = max(W, min(big.width, round(big.width / z)))
            ch = min(big.height, round(cw * H / W))
            x = round((big.width - cw) * (0.15 + 0.7 * t))
            y = (big.height - ch) // 2
            f = big.crop((x, y, x + cw, y + ch)).resize((W, H), Image.LANCZOS)
            caption(f, title, sub)
            yield f, i, n
        return
    # tarjeta: fondo desenfocado + foto enmarcada con zoom suave
    bg = cover(src, W, H).filter(ImageFilter.GaussianBlur(22))
    bg = Image.blend(bg, Image.new("RGB", (W, H), DARK), 0.45)
    card_w = 760
    card_h = round(card_w * src.height / src.width)
    if card_h > 470:
        card_h = 470
        card_w = round(card_h * src.width / src.height)
    photo = src.resize((card_w, card_h), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 80, 2))
    mask = Image.new("L", photo.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, card_w - 1, card_h - 1), 22, fill=255)
    shadow = Image.new("RGBA", (card_w + 80, card_h + 80), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((40, 50, card_w + 40, card_h + 50), 26, fill=(0, 0, 0, 150))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    for i in range(n):
        t = i / max(1, n - 1)
        z = 1.0 + 0.06 * t
        pw, ph = round(card_w * z), round(card_h * z)
        p = photo.resize((pw, ph), Image.BILINEAR)
        m = mask.resize((pw, ph), Image.BILINEAR)
        f = bg.copy()
        top = 40 + (470 - ph) // 2
        f.paste(shadow, ((W - card_w - 80) // 2, top - 40), shadow)
        f.paste(p, ((W - pw) // 2, top), m)
        caption(f, title, sub)
        yield f, i, n


def fade(f: Image.Image, i: int, n: int, k: int = 8) -> Image.Image:
    a = min(1.0, (i + 1) / k, (n - i) / k)
    return f if a >= 1 else Image.blend(Image.new("RGB", (W, H)), f, a)


def ts(sec: float) -> str:
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}"


# ------------------------------------------------------------------ principal
def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="eke-video-"))
    lead, tail = 0.5, 0.9
    timeline, parts, vtt = [], [], ["WEBVTT", ""]
    t = 0.0
    for k, (kind, img, title, sub, text) in enumerate(SCENES):
        wav = tmp / f"s{k}.wav"
        dur = speak(text, wav)
        scene_len = lead + dur + tail
        parts.append((wav, scene_len))
        timeline.append(scene_len)
        vtt += [f"{k + 1}", f"{ts(t + lead)} --> {ts(t + lead + dur)}", text, ""]
        print(f"Escena {k + 1}: {title:32s} {scene_len:5.1f} s")
        t += scene_len
    narration = tmp / "narracion.wav"
    join_audio(parts, narration, lead)

    out = OUT_DIR / f"{NAME}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(narration),
           "-c:v", "libx264", "-preset", "medium", "-crf", "26", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", "-shortest", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    poster_saved = False
    for (kind, img, title, sub, _), seconds in zip(SCENES, timeline):
        for f, i, n in scene_frames(kind, img, title, sub, seconds):
            if kind == "full" and not poster_saved and i == n // 3:
                f.save(ROOT / "src" / "static" / "img" / "video-poster-eke.webp", "WEBP", quality=80)
                poster_saved = True
            proc.stdin.write(fade(f, i, n).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg falló")
    (OUT_DIR / f"{NAME}.vtt").write_text("\n".join(vtt), encoding="utf-8")
    total = sum(timeline)
    meta = {"duration_seconds": round(total, 1), "iso_duration": f"PT{int(total // 60)}M{int(total % 60)}S"}
    (OUT_DIR / f"{NAME}.json").write_text(json.dumps(meta), encoding="utf-8")
    print(f"\nVideo: {out} ({out.stat().st_size / 1e6:.1f} MB, {total:.1f} s)")


if __name__ == "__main__":
    main()

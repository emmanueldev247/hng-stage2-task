from typing import List, Tuple
from pathlib import Path
from datetime import datetime, timezone

from PIL import Image, ImageDraw, ImageFont

CACHE_PATH = Path("cache")
SUMMARY_PATH = CACHE_PATH / "summary.png"

def ensure_cache_dir():
    CACHE_PATH.mkdir(parents=True, exist_ok=True)

def generate_summary_image(total: int, top5: List[Tuple[str, float]], ts: datetime):
    ensure_cache_dir()

    width, height = 900, 520
    img = Image.new("RGB", (width, height), color=(245, 247, 250))
    draw = ImageDraw.Draw(img)
    header_font = ImageFont.load_default()
    body_font = ImageFont.load_default()

    # Header
    draw.text((30, 30), "Country Cache Summary", fill=(20, 20, 20), font=header_font)
    draw.text((30, 70), f"Total Countries: {total}", fill=(20, 20, 20), font=body_font)

    # Top 5
    y = 120
    draw.text((30, y), "Top 5 by estimated GDP:", fill=(20, 20, 20), font=body_font)
    y += 30
    if not top5:
        draw.text((50, y), "No data", fill=(80, 80, 80), font=body_font)
        y += 20
    else:
        for i, (name, gdp) in enumerate(top5, start=1):
            draw.text((50, y), f"{i}. {name} — {gdp:,.2f}", fill=(40, 40, 40), font=body_font)
            y += 24

    # Timestamp (UTC)
    ts_iso = ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    draw.text((30, height - 50), f"Last refresh: {ts_iso}", fill=(100, 100, 100), font=body_font)

    img.save(SUMMARY_PATH)

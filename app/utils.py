from pathlib import Path
from uuid import uuid4
from PIL import Image, ImageSequence
import cv2
import numpy as np

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "webp", "gif", "tif", "tiff"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def unique_name(filename: str) -> str:
    ext = filename.rsplit(".", 1)[1].lower()
    return f"{uuid4().hex}.{ext}"


def read_image(path: str) -> np.ndarray:
    """Reads jpg/png/webp/bmp/tiff/gif. GIF uses first frame. Returns BGR image."""
    suffix = Path(path).suffix.lower()
    if suffix == ".gif":
        img = Image.open(path)
        frame = next(ImageSequence.Iterator(img)).convert("RGB")
        return cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)

    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        pil = Image.open(path).convert("RGB")
        img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    return img


def resize_for_speed(img: np.ndarray, max_side: int = 900) -> np.ndarray:
    h, w = img.shape[:2]
    scale = max_side / max(h, w)
    if scale >= 1:
        return img.copy()
    return cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)


def save_result_image(path: str, image: np.ndarray) -> str:
    cv2.imwrite(path, image)
    return path


def to_percent(value: float) -> float:
    return round(float(value) * 100, 2)

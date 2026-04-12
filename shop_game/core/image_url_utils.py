from __future__ import annotations

from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image, UnidentifiedImageError

MAX_DOWNLOAD_TIMEOUT_SECONDS = 12
DEFAULT_CHUNK_SIZE = 64 * 1024

FORMAT_TO_MIME = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "GIF": "image/gif",
    "WEBP": "image/webp",
    "ICO": "image/x-icon",
}

FORMAT_TO_EXTENSION = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "GIF": ".gif",
    "WEBP": ".webp",
    "ICO": ".ico",
}

MIME_ALIASES = {
    "image/jpg": "image/jpeg",
    "image/pjpeg": "image/jpeg",
    "image/x-png": "image/png",
    "image/vnd.microsoft.icon": "image/x-icon",
}


def _normalize_mime(mime_value: str | None) -> str:
    if not mime_value:
        return ""
    lowered = mime_value.lower().strip()
    return MIME_ALIASES.get(lowered, lowered)


def _build_safe_filename(url: str, image_format: str) -> str:
    parsed = urlparse(url)
    base_name = Path(parsed.path).name
    extension = FORMAT_TO_EXTENSION.get(image_format, ".img")
    if not base_name:
        return f"image_{uuid4().hex[:10]}{extension}"

    candidate = Path(base_name)
    stem = candidate.stem or f"image_{uuid4().hex[:10]}"
    return f"{stem[:80]}{extension}"


def download_image_from_url(
    *,
    image_url: str,
    field_label: str,
    max_size_bytes: int,
    allowed_mime_types: set[str],
) -> SimpleUploadedFile:
    image_url = (image_url or "").strip()
    parsed = urlparse(image_url)
    if parsed.scheme not in ("http", "https"):
        raise ValidationError(f"{field_label}: Link ảnh phải bắt đầu bằng http:// hoặc https://")

    normalized_allowed = {_normalize_mime(item) for item in allowed_mime_types}

    request = Request(
        image_url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; ShoBanAccBot/1.0)"},
    )

    try:
        with urlopen(request, timeout=MAX_DOWNLOAD_TIMEOUT_SECONDS) as response:
            data = bytearray()
            while True:
                chunk = response.read(DEFAULT_CHUNK_SIZE)
                if not chunk:
                    break
                data.extend(chunk)
                if len(data) > max_size_bytes:
                    max_mb = max_size_bytes // (1024 * 1024)
                    raise ValidationError(f"{field_label}: Kích thước ảnh không được vượt quá {max_mb}MB")
    except HTTPError as exc:
        raise ValidationError(f"{field_label}: Không tải được ảnh từ URL (HTTP {exc.code})") from exc
    except URLError as exc:
        raise ValidationError(f"{field_label}: Không thể kết nối tới URL ảnh") from exc
    except TimeoutError as exc:
        raise ValidationError(f"{field_label}: Hết thời gian chờ khi tải ảnh") from exc

    if not data:
        raise ValidationError(f"{field_label}: URL ảnh không có dữ liệu")

    try:
        with Image.open(BytesIO(data)) as image_obj:
            image_obj.verify()
            image_format = (image_obj.format or "").upper()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValidationError(f"{field_label}: URL không phải là ảnh hợp lệ") from exc

    detected_mime = FORMAT_TO_MIME.get(image_format, "")
    if not detected_mime or _normalize_mime(detected_mime) not in normalized_allowed:
        allowed_human = ", ".join(sorted(normalized_allowed))
        raise ValidationError(
            f"{field_label}: Định dạng ảnh không được hỗ trợ. Chấp nhận: {allowed_human}"
        )

    filename = _build_safe_filename(image_url, image_format)
    return SimpleUploadedFile(
        name=filename,
        content=bytes(data),
        content_type=detected_mime,
    )

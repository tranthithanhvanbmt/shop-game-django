from pathlib import Path
from random import randint
import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from shop_game.shop.models import AccountInventory, GameCategory


DEFAULT_CATEGORIES = [
    {
        "name": "Lien Quan Mobile",
        "description": "Kho nick Lien Quan da duyet san, cap nhat lien tuc.",
    },
    {
        "name": "Free Fire",
        "description": "Danh muc tai khoan Free Fire gia tot.",
    },
    {
        "name": "PUBG Mobile",
        "description": "Tai khoan PUBG Mobile da duyet.",
    },
    {
        "name": "Toc Chien",
        "description": "Kho nick LMHT Toc Chien.",
    },
]


def build_details(index: int, skin_name: str, rank: str, win_rate: str, min_price: int, max_price: int) -> str:
    return (
        f"TAI KHOAN {index:02d}: SIEU PHAM {skin_name}\n"
        f"Tuong: 96 | Trang phuc: 91\n\n"
        f"Rank hien tai: {rank} | Ty le thang: {win_rate}\n\n"
        f"Tieu diem Skin:\n"
        f"* Kiemono (Skin hiem bac SS)\n"
        f"* My Melody's Love (Collab Sanrio gioi han)\n"
        f"* Shion (Collab Tensura)\n"
        f"* Cap doi Xa Than/Hoa Tieu Mong Gioi (S+ huu han)\n\n"
        f"Gia mong muon: {min_price:,}d - {max_price:,}d"
    )


def parse_int(value, default=0):
    if value is None:
        return default
    text = str(value).strip().replace(",", "")
    if not text:
        return default
    try:
        return int(text)
    except ValueError:
        return default


def build_details_from_meta(index: int, meta: dict, min_price: int, max_price: int) -> str:
    title = (meta.get("title") or f"TAI KHOAN {index:02d}: SIEU PHAM MY MELODY & KIEMONO").strip()
    heroes = (meta.get("heroes") or "96").strip()
    skins = (meta.get("skins") or "91").strip()
    rank = (meta.get("rank") or "Cao Thu").strip()
    win_rate = (meta.get("win_rate") or "53.2%").strip()
    focus_skins = (meta.get("focus_skins") or "Kiemono (Skin hiem bac SS); My Melody's Love (Collab Sanrio gioi han); Shion (Collab Tensura); Cap doi Xa Than/Hoa Tieu Mong Gioi (S+ huu han)").strip()

    lines = [f"* {item.strip()}" for item in focus_skins.split(";") if item.strip()]
    focus_block = "\n".join(lines) if lines else "* Kiemono (Skin hiem bac SS)"

    return (
        f"{title}\n"
        f"Tuong: {heroes} | Trang phuc: {skins}\n\n"
        f"Rank hien tai: {rank} | Ty le thang: {win_rate}\n\n"
        f"Tieu diem Skin:\n"
        f"{focus_block}\n\n"
        f"Gia mong muon: {min_price:,}d - {max_price:,}d"
    )


class Command(BaseCommand):
    help = "Tao danh muc game va tao kho nick tu anh trong media/import_nicks"

    def add_arguments(self, parser):
        parser.add_argument(
            "--category",
            default="lien-quan-mobile",
            help="Slug danh muc de tao nick (mac dinh: lien-quan-mobile)",
        )
        parser.add_argument(
            "--source",
            default="media/import_nicks",
            help="Thu muc chua anh goc de import (mac dinh: media/import_nicks)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Gioi han so luong nick tao, 0 = khong gioi han",
        )
        parser.add_argument(
            "--min-price",
            type=int,
            default=450000,
            help="Gia toi thieu de random",
        )
        parser.add_argument(
            "--max-price",
            type=int,
            default=600000,
            help="Gia toi da de random",
        )
        parser.add_argument(
            "--metadata",
            default="media/import_nicks/metadata.csv",
            help="File CSV chua noi dung theo tung anh",
        )

    def handle(self, *args, **options):
        self._ensure_categories()

        category_slug = options["category"]
        source_dir = (Path(settings.BASE_DIR) / options["source"]).resolve()
        limit = options["limit"]
        min_price = options["min_price"]
        max_price = options["max_price"]
        metadata_path = (Path(settings.BASE_DIR) / options["metadata"]).resolve()

        if min_price > max_price:
            self.stderr.write(self.style.ERROR("--min-price khong duoc lon hon --max-price"))
            return

        category = GameCategory.objects.filter(slug=category_slug).first()
        if not category:
            self.stderr.write(self.style.ERROR(f"Khong tim thay danh muc slug='{category_slug}'"))
            return

        if not source_dir.exists():
            source_dir.mkdir(parents=True, exist_ok=True)
            self.stdout.write(self.style.WARNING(
                f"Da tao thu muc {source_dir}. Hay copy anh vao day roi chay lai lenh."
            ))
            return

        image_paths = sorted(
            [
                p
                for p in source_dir.iterdir()
                if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
            ]
        )

        metadata_map = self._load_metadata(metadata_path)

        if not image_paths:
            self.stdout.write(self.style.WARNING("Khong co anh nao trong thu muc import."))
            return

        if limit > 0:
            image_paths = image_paths[:limit]

        created = 0
        for idx, image_path in enumerate(image_paths, start=1):
            rel_media_path = image_path.relative_to(Path(settings.BASE_DIR) / "media").as_posix()
            key = image_path.name.lower()
            meta = metadata_map.get(key, {})

            login_name = (meta.get("username") or f"lq_acc_{idx:03d}").strip()
            password = (meta.get("password") or f"LQ{idx:03d}@Shop").strip()
            rank = (meta.get("rank") or "Cao Thu").strip()
            login_method = (meta.get("login_method") or "Garena").strip()
            details = build_details_from_meta(idx, meta, min_price, max_price)

            fixed_price = parse_int(meta.get("price"), default=0)
            local_min = parse_int(meta.get("price_min"), default=min_price)
            local_max = parse_int(meta.get("price_max"), default=max_price)
            if local_min > local_max:
                local_min, local_max = local_max, local_min
            price = fixed_price if fixed_price > 0 else randint(local_min, local_max)

            exists = AccountInventory.objects.filter(
                category=category,
                username=login_name,
            ).exists()
            if exists:
                continue

            AccountInventory.objects.create(
                category=category,
                username=login_name,
                password=password,
                login_method=login_method,
                price=price,
                rank=rank,
                details=details,
                image_thumb=rel_media_path,
                image_1=rel_media_path,
                status="AVAILABLE",
                is_approved=True,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Tao {created} nick moi trong danh muc '{category.name}'."
        ))

    def _load_metadata(self, metadata_path: Path):
        if not metadata_path.exists():
            return {}

        rows = {}
        with metadata_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                filename = (row.get("filename") or "").strip().lower()
                if not filename:
                    continue
                rows[filename] = row
        return rows

    def _ensure_categories(self):
        for item in DEFAULT_CATEGORIES:
            slug = slugify(item["name"])
            GameCategory.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": item["name"],
                    "description": item["description"],
                    "is_active": True,
                },
            )

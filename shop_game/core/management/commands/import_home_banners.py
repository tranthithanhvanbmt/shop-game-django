from pathlib import Path
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

from shop_game.core.models import Banner


class Command(BaseCommand):
    help = "Import anh banner trang chu tu thu muc media/import_banners vao bang Banner"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            default="media/import_banners",
            help="Thu muc chua anh goc",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Xoa toan bo banner cu truoc khi import",
        )
        parser.add_argument(
            "--link",
            default="",
            help="Gan link mac dinh cho banner moi",
        )
        parser.add_argument(
            "--inactive",
            action="store_true",
            help="Tao banner o trang thai tat (is_active=False)",
        )

    def handle(self, *args, **options):
        source_dir = (Path(settings.BASE_DIR) / options["source"]).resolve()
        media_root = Path(settings.MEDIA_ROOT)
        banners_dir = media_root / "banners"
        banners_dir.mkdir(parents=True, exist_ok=True)

        if not source_dir.exists():
            source_dir.mkdir(parents=True, exist_ok=True)
            self.stdout.write(self.style.WARNING(
                f"Da tao {source_dir}. Ban copy anh banner vao day roi chay lai lenh."
            ))
            return

        image_files = sorted(
            [
                p
                for p in source_dir.iterdir()
                if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif"}
            ]
        )

        if not image_files:
            self.stdout.write(self.style.WARNING("Khong tim thay anh banner de import."))
            return

        if options["clear"]:
            Banner.objects.all().delete()

        default_link = options["link"].strip()
        is_active = not options["inactive"]
        next_order = (Banner.objects.order_by("-order").values_list("order", flat=True).first() or 0) + 1

        created = 0
        for image in image_files:
            destination = banners_dir / image.name
            if image.resolve() != destination.resolve():
                shutil.copy2(image, destination)

            banner_rel = f"banners/{image.name}"
            title = image.stem.replace("_", " ").replace("-", " ").strip().title()

            exists = Banner.objects.filter(image=banner_rel).exists()
            if exists:
                continue

            Banner.objects.create(
                title=title,
                image=banner_rel,
                link=default_link,
                is_active=is_active,
                order=next_order,
            )
            next_order += 1
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Da import {created} banner moi."))

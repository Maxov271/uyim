"""Seeds the database with data matching frontend/assets/js/data.js exactly — same cities,
districts, mahallas, banks, agents/agencies and listings — so switching the frontend from
the mock data.js to the real API produces the identical catalogue out of the box.
"""

from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

CITIES = [
    ("tashkent", "Toshkent", 41.2995, 69.2401, 11),
    ("samarkand", "Samarqand", 39.6542, 66.9597, 12),
    ("bukhara", "Buxoro", 39.7747, 64.4286, 12),
    ("andijan", "Andijon", 40.7821, 72.3442, 12),
    ("fergana", "Farg'ona", 40.3864, 71.7864, 12),
    ("namangan", "Namangan", 40.9983, 71.6726, 12),
    ("nukus", "Nukus", 42.4600, 59.6166, 12),
    ("qarshi", "Qarshi", 38.8600, 65.7890, 12),
    ("urgench", "Urganch", 41.5500, 60.6333, 12),
    ("termiz", "Termiz", 37.2242, 67.2783, 12),
]

DISTRICTS = [
    ("chilonzor", "tashkent", "Chilonzor", 41.2750, 69.2050,
     ["Qatortol", "Novza", "Oqqo'rg'on", "Chilonzor-19", "Xalqlar do'stligi"]),
    ("yunusobod", "tashkent", "Yunusobod", 41.3600, 69.2890,
     ["Bodomzor", "Minor", "Turkiston", "Yunusobod-4", "Shifokorlar"]),
    ("mirzo-ulugbek", "tashkent", "Mirzo Ulug'bek", 41.3300, 69.3400,
     ["Buyuk Ipak Yo'li", "Qorasuv", "Feruza", "Universitet"]),
    ("yakkasaroy", "tashkent", "Yakkasaroy", 41.2830, 69.2560,
     ["Shota Rustaveli", "Bobur", "Qushbegi", "Yakkasaroy markaz"]),
    ("shayxontohur", "tashkent", "Shayxontohur", 41.3200, 69.2200,
     ["Chorsu", "Beruniy", "Zarqaynar", "Ko'kcha"]),
    ("mirobod", "tashkent", "Mirobod", 41.2900, 69.2900,
     ["Salar", "Temir yo'l", "Oybek", "Mirobod markaz"]),
    ("olmazor", "tashkent", "Olmazor", 41.3500, 69.2100,
     ["Qora qamish", "Tinchlik", "Olmazor markaz"]),
    ("uchtepa", "tashkent", "Uchtepa", 41.2900, 69.1700,
     ["Chinobod", "Xonobod", "Uchtepa-6"]),
    ("sergeli", "tashkent", "Sergeli", 41.2200, 69.2200,
     ["Sergeli-7", "Yangihayot", "Quruvchi"]),
    ("yashnobod", "tashkent", "Yashnobod", 41.2800, 69.3300,
     ["Tuzel", "Parkent", "Yashnobod markaz"]),
    ("bektemir", "tashkent", "Bektemir", 41.2100, 69.3400,
     ["Bektemir markaz", "Kimyogar"]),
]

BANKS = [
    ("ipoteka", "Ipoteka Bank", 17.0, 15, 20, "Yangi bino uchun 15% boshlang'ich"),
    ("xalq", "Xalq Banki", 18.5, 20, 15, "Ikkilamchi bozor uchun ham amal qiladi"),
    ("qqb", "Qishloq Qurilish Bank", 16.5, 25, 20, "Tumanlarda qurilish uchun imtiyoz"),
    ("agro", "Agrobank", 19.0, 20, 12, "Tez ko'rib chiqish · 3 kun"),
    ("sqb", "SQB", 18.0, 20, 15, "Onlayn oldindan tasdiqlash"),
    ("subsidy", "Subsidiya (davlat dasturi)", 10.0, 15, 20, "Yosh oilalar uchun cheklangan kvota"),
]

DEVELOPERS = [
    ("Golden House", 12, "tashkent"),
    ("Murad Buildings", 8, "tashkent"),
    ("Akay Group", 6, "tashkent"),
    ("NRG Group", 9, "tashkent"),
    ("Orient Group", 5, "samarkand"),
    ("Qurilish Trest-12", 4, "bukhara"),
]

# owners: phone, name, role, agency(name/inn/years/rating) or None, telegram_username
OWNERS = {
    "a1": dict(phone="+998901234567", name="Golden House", role="agency",
               agency=dict(name="Golden House Agency", inn="123456789", years=4, rating=4.8, verified=True),
               tg="goldenhouse_uz"),
    "a2": dict(phone="+998935552109", name="Dilshod Karimov", role="owner", agency=None, tg="dilshod_uy"),
    "a3": dict(phone="+998712003040", name="Makon Realty", role="agency",
               agency=dict(name="Makon Realty", inn="987654321", years=6, rating=4.6, verified=True),
               tg="makon_realty"),
    "a4": dict(phone="+998998104412", name="Zarnigor Yusupova", role="owner", agency=None, tg=""),
}

# id, deal, type, price, rooms, area, floor, floors, district, mahalla, lat, lng, owner_key, overrides
LISTINGS = [
    ("l1", "sale", "Kvartira", 82000, 3, 78, 9, 12, "chilonzor", "Qatortol", 41.2762, 69.2043, "a1",
     dict(top_until_days=7, metro_name="Novza", metro_minutes=8, views=1240)),
    ("l2", "sale", "Kvartira", 64500, 2, 54, 4, 9, "chilonzor", "Novza", 41.2721, 69.2101, "a2",
     dict(hot_until_days=3, condition="O'rta ta'mir", views=960)),
    ("l3", "new", "Kvartira", 118000, 4, 102, 7, 16, "yunusobod", "Bodomzor", 41.3591, 69.2872, "a3",
     dict(top_until_days=7, year=2026, condition="Qurilish tugagan", views=1580)),
    ("l4", "sale", "Kvartira", 96000, 3, 84, 11, 14, "mirzo-ulugbek", "Buyuk Ipak Yo'li", 41.3312, 69.3388, "a1",
     dict(metro_name="BIY", metro_minutes=5, views=720)),
    ("l5", "rent", "Kvartira", 640, 2, 58, 3, 5, "yakkasaroy", "Shota Rustaveli", 41.2836, 69.2564, "a1",
     dict(metro_name="Kosmonavtlar", metro_minutes=6, mortgage_allowed=False, views=410)),
    ("l6", "daily", "Kvartira", 38, 1, 42, 2, 4, "mirobod", "Oybek", 41.2913, 69.2887, "a3",
     dict(mortgage_allowed=False, views=290)),
    ("l7", "sale", "Hovli uy", 175000, 5, 180, 1, 2, "olmazor", "Tinchlik", 41.3512, 69.2088, "a1",
     dict(year=2015, features=["Hovli 6 sotix", "Garaj", "Issiqxona", "Quduq"], views=530)),
    ("l8", "new", "Kvartira", 72000, 2, 61, 12, 18, "sergeli", "Yangihayot", 41.2214, 69.2189, "a3",
     dict(year=2026, condition="Oq holat", views=880)),
    ("l9", "sale", "Kvartira", 58000, 2, 50, 2, 4, "uchtepa", "Chinobod", 41.2894, 69.1712, "a4",
     dict(verified_owner=False, condition="Ta'mir talab", views=340)),
    ("l10", "commercial", "Tijorat", 240000, 0, 220, 1, 3, "shayxontohur", "Chorsu", 41.3196, 69.2213, "a1",
     dict(features=["Ko'cha chizig'i", "Alohida kirish", "3 fazali quvvat"], views=610)),
    ("l11", "sale", "Kvartira", 134000, 4, 110, 5, 9, "mirobod", "Salar", 41.2905, 69.2921, "a3",
     dict(top_until_days=7, views=1120)),
    ("l12", "rent", "Hovli uy", 1200, 4, 150, 1, 2, "yunusobod", "Minor", 41.3628, 69.2841, "a1",
     dict(mortgage_allowed=False, views=250)),
    ("l13", "land", "Yer uchastkasi", 45000, 0, 600, 0, 0, "yashnobod", "Parkent", 41.2814, 69.3312, "a1",
     dict(features=["8 sotix", "Kadastr tayyor", "Yo'l chizig'i"], mortgage_allowed=False, views=300)),
    ("l14", "new", "Kvartira", 89000, 3, 76, 3, 16, "chilonzor", "Chilonzor-19", 41.2788, 69.1998, "a3",
     dict(year=2025, hot_until_days=3, views=1010)),
]

DEFAULT_FEATURES = ["Konditsioner", "Mebelli", "Parking", "Yopiq hovli", "Internet · optika"]
DEFAULT_DESC = (
    "Tinch hovlida joylashgan yorug' kvartira. Oshxona jihozlangan, konditsioner va "
    "o'rnatilgan mebel qoladi. Hujjatlar tayyor — kadastr va notarial oldi-sotdiga to'liq mos."
)

TELEGRAM_CHANNELS = [
    ("chilonzor_uylar", "chilonzor"),
    ("yunusobod_uylar", "yunusobod"),
    ("mirobod_uylar", "mirobod"),
]


class Command(BaseCommand):
    help = "Demo ma'lumotlar bilan bazani to'ldiradi (frontend/assets/js/data.js bilan bir xil)"

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="Avval mavjud demo ma'lumotlarni tozalash")

    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model

        from apps.agencies.models import Agency
        from apps.developers.models import Developer
        from apps.geo.models import City, District, Mahalla
        from apps.listings.models import Listing, ListingPhoto
        from apps.mortgage.models import Bank
        from apps.telegrambot.models import TelegramChannel

        User = get_user_model()
        now = timezone.now()

        self.stdout.write("Geo...")
        city_objs = {}
        for cid, name, lat, lng, zoom in CITIES:
            city_objs[cid] = City.objects.update_or_create(
                id=cid, defaults={"name": name, "lat": lat, "lng": lng, "zoom": zoom}
            )[0]

        district_objs = {}
        for did, city_id, name, lat, lng, mahallas in DISTRICTS:
            district = District.objects.update_or_create(
                id=did, defaults={"city": city_objs[city_id], "name": name, "lat": lat, "lng": lng}
            )[0]
            district_objs[did] = district
            for mname in mahallas:
                Mahalla.objects.update_or_create(district=district, name=mname)

        self.stdout.write("Banklar...")
        for bid, name, rate, min_down, max_term, note in BANKS:
            Bank.objects.update_or_create(
                id=bid,
                defaults={
                    "name": name, "rate": Decimal(str(rate)), "min_down_pct": min_down,
                    "max_term_years": max_term, "note": note, "active": True,
                },
            )

        self.stdout.write("Quruvchilar...")
        for name, count, city_id in DEVELOPERS:
            dev, _ = Developer.objects.update_or_create(
                name=name, defaults={"city": city_objs[city_id]}
            )
            from apps.developers.models import Project

            existing = dev.projects.count()
            for i in range(existing, count):
                Project.objects.create(
                    developer=dev, name=f"{name} loyiha {i + 1}",
                    city=city_objs[city_id], district=list(district_objs.values())[0],
                    stage=Project.Stage.IN_PROGRESS,
                )

        self.stdout.write("Egalar/agentliklar...")
        owner_objs = {}
        for key, info in OWNERS.items():
            user, _ = User.objects.update_or_create(
                phone=info["phone"],
                defaults={
                    "name": info["name"], "role": info["role"], "verified_phone": True,
                    "telegram_username": info["tg"], "city": city_objs["tashkent"],
                },
            )
            if info["agency"]:
                Agency.objects.update_or_create(
                    user=user,
                    defaults={
                        "name": info["agency"]["name"], "inn": info["agency"]["inn"],
                        "years": info["agency"]["years"], "rating": Decimal(str(info["agency"]["rating"])),
                        "verified": info["agency"]["verified"],
                    },
                )
            owner_objs[key] = user

        self.stdout.write("Telegram kanallari...")
        for username, did in TELEGRAM_CHANNELS:
            TelegramChannel.objects.update_or_create(
                username=f"@{username}", defaults={"district": district_objs[did], "active": True}
            )

        self.stdout.write("E'lonlar...")
        for lid, deal, ptype, price, rooms, area, floor, floors, did, mahalla, lat, lng, owner_key, ov in LISTINGS:
            district = district_objs[did]
            owner = owner_objs[owner_key]
            defaults = {
                "owner": owner,
                "agency": getattr(owner, "agency", None),
                "deal": deal,
                "type": ptype,
                "price_usd": Decimal(str(price)),
                "rooms": rooms,
                "area": Decimal(str(area)),
                "floor": floor,
                "floors": floors,
                "year": ov.get("year", 2019),
                "condition": ov.get("condition", "Evro ta'mir"),
                "city": district.city,
                "district": district,
                "mahalla": mahalla,
                "lat": lat,
                "lng": lng,
                "metro_name": ov.get("metro_name", ""),
                "metro_minutes": ov.get("metro_minutes"),
                "mortgage_allowed": ov.get("mortgage_allowed", True),
                "verified_owner": ov.get("verified_owner", True),
                "features": ov.get("features", DEFAULT_FEATURES),
                "description": DEFAULT_DESC,
                "status": Listing.Status.ACTIVE,
                "views": ov.get("views", 0),
            }
            listing, created = Listing.objects.update_or_create(
                owner=owner, district=district, mahalla=mahalla, rooms=rooms, area=Decimal(str(area)),
                defaults=defaults,
            )
            if created or not listing.published_at:
                Listing.objects.filter(pk=listing.pk).update(
                    published_at=now - timedelta(days=3), created_at=now - timedelta(days=3)
                )
            if "top_until_days" in ov:
                listing.top_until = now + timedelta(days=ov["top_until_days"])
            if "hot_until_days" in ov:
                listing.hot_until = now + timedelta(days=ov["hot_until_days"])
            listing.save()

            if not listing.photos.exists():
                for i in range(3):
                    ListingPhoto.objects.create(
                        listing=listing, image=self._placeholder_image(), order=i, is_cover=(i == 0)
                    )

        self.stdout.write(self.style.SUCCESS("Demo ma'lumotlar tayyor."))

    @staticmethod
    def _placeholder_image():
        """A tiny 1x1 PNG so ListingPhoto.image always resolves to a real file in dev."""
        import base64

        from django.core.files.base import ContentFile

        png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
        )
        return ContentFile(png, name="placeholder.png")

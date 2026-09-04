from django.db import models


class Developer(models.Model):
    name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to="developer_logos/", null=True, blank=True)
    city = models.ForeignKey("geo.City", on_delete=models.PROTECT, related_name="developers")
    description = models.TextField(blank=True)
    founded_year = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Project(models.Model):
    class Stage(models.TextChoices):
        PLANNED = "planned", "Qurilish boshlanmagan"
        IN_PROGRESS = "in_progress", "Qurilish jarayonida"
        COMPLETED = "completed", "Qurilish tugagan"

    developer = models.ForeignKey(Developer, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=150)
    city = models.ForeignKey("geo.City", on_delete=models.PROTECT, related_name="projects")
    district = models.ForeignKey("geo.District", on_delete=models.PROTECT, related_name="projects")
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    stage = models.CharField(max_length=16, choices=Stage.choices, default=Stage.PLANNED)
    completion_label = models.CharField(max_length=32, blank=True, help_text="masalan: 2026 Q3")
    price_from_usd = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    installment_available = models.BooleanField(default=False)
    tour_3d_url = models.URLField(blank=True)
    cover_image = models.ImageField(upload_to="projects/", null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.name} · {self.developer_id}"

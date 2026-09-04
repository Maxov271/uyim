from django.db import models


class City(models.Model):
    id = models.SlugField(primary_key=True, max_length=32)
    name = models.CharField(max_length=100)
    lat = models.FloatField()
    lng = models.FloatField()
    zoom = models.PositiveSmallIntegerField(default=12)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name


class District(models.Model):
    id = models.SlugField(primary_key=True, max_length=48)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="districts")
    name = models.CharField(max_length=100)
    lat = models.FloatField()
    lng = models.FloatField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.city_id})"


class Mahalla(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="mahallas")
    name = models.CharField(max_length=120)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = [("district", "name")]
        verbose_name_plural = "Mahallas"

    def __str__(self):
        return f"{self.name} · {self.district_id}"

import os
from django.conf import settings
from django.db import models

class DetectionHistory(models.Model):
    filename = models.CharField(max_length=255)
    filepath = models.CharField(max_length=500, blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    result = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.filename} - {self.result} at {self.timestamp}"

    def delete(self, *args, **kwargs):
        if self.filepath:
            full_path = os.path.join(settings.MEDIA_ROOT, self.filepath)
            if os.path.exists(full_path):
                os.remove(full_path)
        super().delete(*args, **kwargs)
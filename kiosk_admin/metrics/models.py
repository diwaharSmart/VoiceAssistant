from django.db import models
from django.utils import timezone

class APIMetric(models.Model):
    application_name = models.CharField(max_length=255, blank=True, null=True)
    vendor_name = models.CharField(max_length=255, blank=True, null=True)
    api_name = models.CharField(max_length=255, blank=True, null=True)
    request_packet = models.TextField(blank=True, null=True)
    response_packet = models.TextField(blank=True, null=True)
    status_code = models.IntegerField(blank=True, null=True)
    elapsed_time = models.FloatField(blank=True, null=True)
    spi_status_code = models.CharField(max_length=50, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    additional_info = models.JSONField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)  # New field

    def __str__(self):
        return f"{self.application_name} - {self.api_name} - {self.timestamp}"
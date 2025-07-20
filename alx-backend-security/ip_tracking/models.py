from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import ipaddress

class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(default=timezone.now)
    path = models.CharField(max_length=255)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.ip_address} - {self.path} - {self.timestamp}"

class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    
    def clean(self):
        try:
            ipaddress.ip_address(self.ip_address)
        except ValueError:
            raise ValidationError("Invalid IP address")
    
    def __str__(self):
        return self.ip_address

class SuspiciousIP(models.Model):
    REASON_CHOICES = [
        ('high_requests', 'High number of requests'),
        ('sensitive_path', 'Accessed sensitive paths'),
    ]
    
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.ip_address} - {self.get_reason_display()}"
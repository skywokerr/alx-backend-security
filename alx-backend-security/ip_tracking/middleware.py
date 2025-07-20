import time
from django.http import HttpResponseForbidden
from django.core.cache import cache
from ip_tracking.models import RequestLog, BlockedIP
from ipgeolocation import IpGeolocationAPI
from django.conf import settings

class IPLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check if IP is blocked before processing
        ip_address = self.get_client_ip(request)
        
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("IP address blocked")
        
        response = self.get_response(request)
        
        # Log the request
        self.log_request(request, ip_address)
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def log_request(self, request, ip_address):
        path = request.path
        
        # Check cache first for geolocation data
        cache_key = f"geo_{ip_address}"
        geo_data = cache.get(cache_key)
        
        if not geo_data and hasattr(settings, 'IPGEOLOCATION_API_KEY'):
            geo_api = IpGeolocationAPI(settings.IPGEOLOCATION_API_KEY)
            geo_data = geo_api.get_geolocation(ip_address=ip_address)
            
            if geo_data and geo_data.get('status') == 'success':
                geo_data = {
                    'country': geo_data.get('country_name'),
                    'city': geo_data.get('city'),
                }
                # Cache for 24 hours (86400 seconds)
                cache.set(cache_key, geo_data, 86400)
            else:
                geo_data = {'country': None, 'city': None}
        
        RequestLog.objects.create(
            ip_address=ip_address,
            path=path,
            country=geo_data.get('country') if geo_data else None,
            city=geo_data.get('city') if geo_data else None
        )
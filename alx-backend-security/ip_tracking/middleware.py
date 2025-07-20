from .models import RequestLog

class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the client's IP address
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            # If behind a proxy, take the first IP in the list
            ip_address = ip_address.split(',')[0].strip()
        else:
            # Otherwise, use REMOTE_ADDR
            ip_address = request.META.get('REMOTE_ADDR')

        # Log the request details
        RequestLog.objects.create(ip_address=ip_address, path=request.path)

        # Proceed with the request
        response = self.get_response(request)
        return response
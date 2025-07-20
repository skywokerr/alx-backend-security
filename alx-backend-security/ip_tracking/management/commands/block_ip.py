from django.core.management.base import BaseCommand
from ip_tracking.models import BlockedIP
import ipaddress

class Command(BaseCommand):
    help = 'Add IP addresses to the blocking list'
    
    def add_arguments(self, parser):
        parser.add_argument('ip_addresses', nargs='+', type=str, help='IP addresses to block')
    
    def handle(self, *args, **options):
        for ip in options['ip_addresses']:
            try:
                # Validate IP address
                ipaddress.ip_address(ip)
                
                BlockedIP.objects.get_or_create(ip_address=ip)
                self.stdout.write(self.style.SUCCESS(f'Successfully blocked IP: {ip}'))
            except ValueError:
                self.stdout.write(self.style.ERROR(f'Invalid IP address: {ip}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error blocking IP {ip}: {str(e)}'))
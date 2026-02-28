"""
Management command to create a superuser for testing
Usage: python manage.py setup_admin
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create a default admin user for testing'
    
    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@bhoomiputhraagri.com'
        password = 'admin123'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists!')
            )
            return
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Superuser created successfully!\n'
                f'   Username: {username}\n'
                f'   Password: {password}\n'
                f'   Email: {email}\n'
            )
        )

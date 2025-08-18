"""
Management command to backup database and media files
"""
import os
import shutil
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import send_mail
import logging

logger = logging.getLogger('ward_system')

class Command(BaseCommand):
    help = 'Backup database and media files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            action='store_true',
            help='Send backup completion email to admin',
        )

    def handle(self, *args, **options):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(settings.BASE_DIR, 'backups', timestamp)
        
        try:
            # Create backup directory
            os.makedirs(backup_dir, exist_ok=True)
            
            # Backup database
            self.backup_database(backup_dir, timestamp)
            
            # Backup media files
            self.backup_media(backup_dir)
            
            # Clean old backups
            self.cleanup_old_backups()
            
            success_msg = f'Backup completed successfully: {backup_dir}'
            self.stdout.write(self.style.SUCCESS(success_msg))
            logger.info(success_msg)
            
            if options['email']:
                self.send_backup_notification(True, backup_dir)
                
        except Exception as e:
            error_msg = f'Backup failed: {str(e)}'
            self.stdout.write(self.style.ERROR(error_msg))
            logger.error(error_msg, exc_info=True)
            
            if options['email']:
                self.send_backup_notification(False, str(e))

    def backup_database(self, backup_dir, timestamp):
        """Backup SQLite database"""
        db_path = settings.DATABASES['default']['NAME']
        backup_path = os.path.join(backup_dir, f'database_{timestamp}.sqlite3')
        
        if os.path.exists(db_path):
            shutil.copy2(db_path, backup_path)
            self.stdout.write(f'Database backed up to: {backup_path}')
        else:
            raise FileNotFoundError(f'Database file not found: {db_path}')

    def backup_media(self, backup_dir):
        """Backup media files"""
        media_root = settings.MEDIA_ROOT
        media_backup_dir = os.path.join(backup_dir, 'media')
        
        if os.path.exists(media_root):
            shutil.copytree(media_root, media_backup_dir)
            self.stdout.write(f'Media files backed up to: {media_backup_dir}')

    def cleanup_old_backups(self):
        """Remove backups older than retention period"""
        backup_root = os.path.join(settings.BASE_DIR, 'backups')
        retention_days = getattr(settings, 'BACKUP_RETENTION_DAYS', 30)
        
        if not os.path.exists(backup_root):
            return
            
        cutoff_time = datetime.now().timestamp() - (retention_days * 24 * 3600)
        
        for backup_folder in os.listdir(backup_root):
            backup_path = os.path.join(backup_root, backup_folder)
            if os.path.isdir(backup_path):
                if os.path.getctime(backup_path) < cutoff_time:
                    shutil.rmtree(backup_path)
                    self.stdout.write(f'Removed old backup: {backup_folder}')

    def send_backup_notification(self, success, details):
        """Send email notification about backup status"""
        subject = 'Ward System Backup ' + ('Successful' if success else 'Failed')
        message = f'Backup details: {details}'
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMINS[0][1]] if settings.ADMINS else [],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f'Failed to send backup notification: {e}')

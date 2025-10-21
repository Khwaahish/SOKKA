from django.core.management.base import BaseCommand
from kanban.models import PipelineStage


class Command(BaseCommand):
    help = 'Initialize pipeline stages for the Kanban board'

    def handle(self, *args, **options):
        stages = [
            ('profile_interest', 'Profile Interest', '#667eea', 0),
            ('resume_review', 'Resume Review', '#43e97b', 1),
            ('interview', 'Interview', '#4facfe', 2),
            ('hired', 'Hired', '#38b2ac', 3),
            ('rejected', 'Rejected', '#fa709a', 4),
        ]
        
        created_count = 0
        for name, display_name, color, order in stages:
            stage, created = PipelineStage.objects.get_or_create(
                name=name,
                defaults={
                    'order': order,
                    'color': color
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created stage: {display_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Stage already exists: {display_name}')
                )
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully created {created_count} pipeline stage(s).')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nAll pipeline stages already exist.')
            )


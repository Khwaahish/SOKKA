from django.core.management.base import BaseCommand
from kanban.models import PipelineStage


class Command(BaseCommand):
    help = 'Populate the pipeline stages for the kanban board'

    def handle(self, *args, **options):
        stages_data = [
            {'name': 'profile_interest', 'order': 0, 'color': '#0079bf'},
            {'name': 'resume_review', 'order': 1, 'color': '#d29034'},
            {'name': 'interview', 'order': 2, 'color': '#8fce00'},
            {'name': 'hired', 'order': 3, 'color': '#61bd4f'},
            {'name': 'rejected', 'order': 4, 'color': '#cf513d'},
        ]
        
        created_count = 0
        for stage_data in stages_data:
            stage, created = PipelineStage.objects.get_or_create(
                name=stage_data['name'],
                defaults={
                    'order': stage_data['order'],
                    'color': stage_data['color']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created stage: {stage.get_name_display()}')
                )
            else:
                # Update existing stage order and color if needed
                if stage.order != stage_data['order'] or stage.color != stage_data['color']:
                    stage.order = stage_data['order']
                    stage.color = stage_data['color']
                    stage.save()
                    self.stdout.write(
                        self.style.WARNING(f'Updated stage: {stage.get_name_display()}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Stage already exists: {stage.get_name_display()}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new pipeline stages')
        )

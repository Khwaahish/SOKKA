# Generated migration to auto-create pipeline stages

from django.db import migrations


def create_pipeline_stages(apps, schema_editor):
    """Create the default pipeline stages if they don't exist"""
    PipelineStage = apps.get_model('kanban', 'PipelineStage')
    
    stages = [
        ('profile_interest', 0, '#667eea'),
        ('resume_review', 1, '#43e97b'),
        ('interview', 2, '#4facfe'),
        ('hired', 3, '#38b2ac'),
        ('rejected', 4, '#fa709a'),
    ]
    
    for name, order, color in stages:
        PipelineStage.objects.get_or_create(
            name=name,
            defaults={
                'order': order,
                'color': color
            }
        )


def reverse_pipeline_stages(apps, schema_editor):
    """Remove the pipeline stages (for rollback)"""
    PipelineStage = apps.get_model('kanban', 'PipelineStage')
    stage_names = ['profile_interest', 'resume_review', 'interview', 'hired', 'rejected']
    PipelineStage.objects.filter(name__in=stage_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_pipeline_stages, reverse_pipeline_stages),
    ]


from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import ProfileCard

from django.db.models.signals import post_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=ProfileCard)
def update_job_application_status(sender, instance, **kwargs):
    """Update the job application status when its card stage changes"""
    if instance.job_application:
        logger.info(f"Updating status for application {instance.job_application.pk} "
                   f"for job {instance.job_application.job.title}")
        instance.job_application.update_status_from_stage(instance.stage)
        logger.info(f"New status: {instance.job_application.status} "
                   f"(Stage: {instance.stage.name})")
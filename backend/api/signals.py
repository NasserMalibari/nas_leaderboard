from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Participant, ParticipantStats

@receiver(post_save, sender=Participant)
def create_participant_stats(sender, instance, created, **kwargs):
    if created:
        ParticipantStats.objects.create(id=instance)
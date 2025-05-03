from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from chigame.games.models import GameList


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_default_favorites_list(sender, instance, created, **kwargs):
    """
    Automatically create a default "Favorites" GameList for new users.
    """
    if created:
        GameList.objects.create(name="Favorites", description="", created_by=instance)

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Listing, PriceHistory

_PRICE_ATTR = "_previous_price_usd"
_STATUS_ATTR = "_previous_status"


@receiver(pre_save, sender=Listing)
def _stash_previous_state(sender, instance: Listing, **kwargs):
    if not instance.pk:
        setattr(instance, _PRICE_ATTR, None)
        setattr(instance, _STATUS_ATTR, None)
        return
    previous = Listing.objects.filter(pk=instance.pk).values("price_usd", "status").first()
    if previous:
        setattr(instance, _PRICE_ATTR, previous["price_usd"])
        setattr(instance, _STATUS_ATTR, previous["status"])


@receiver(post_save, sender=Listing)
def _track_price_and_publish(sender, instance: Listing, created: bool, **kwargs):
    previous_price = getattr(instance, _PRICE_ATTR, None)
    price_changed = previous_price is not None and previous_price != instance.price_usd
    if created or price_changed:
        PriceHistory.objects.create(listing=instance, price_usd=instance.price_usd)

    previous_status = getattr(instance, _STATUS_ATTR, None)
    just_activated = instance.status == Listing.Status.ACTIVE and previous_status != Listing.Status.ACTIVE
    just_archived = instance.status == Listing.Status.ARCHIVED and previous_status not in (
        None, Listing.Status.ARCHIVED,
    )

    from apps.telegrambot.tasks import (
        mark_listing_sold,
        notify_saved_searches,
        publish_listing_to_channel,
        update_listing_posts,
    )

    if just_activated:
        if not instance.published_at:
            Listing.objects.filter(pk=instance.pk).update(published_at=timezone.now())
        publish_listing_to_channel.delay(instance.id)
        notify_saved_searches.delay(instance.id)
    elif just_archived:
        mark_listing_sold.delay(instance.id)
    elif price_changed and instance.status == Listing.Status.ACTIVE:
        update_listing_posts.delay(instance.id)

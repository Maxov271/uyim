from celery import shared_task

from .currency import sync_usd_rate


@shared_task
def sync_usd_rate_task():
    sync_usd_rate()

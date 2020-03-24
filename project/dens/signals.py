from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .consumers import den_fetch, index_fetch, IndexConsumer
from .models import ChatMessageModel, DenConnectionModel, DenModel


@receiver(post_delete, sender=DenModel)
def delete_den_model_hook(sender, instance, using, **kwargs):
    layer = get_channel_layer()

    async_to_sync(layer.group_send)(
        'den_%s' % instance.slug,
        {
            'type': 'redirect',
        }
    )

    index_data = index_fetch()
    async_to_sync(layer.group_send)(
        IndexConsumer.group_name,
        {
            'type': 'update',
            'data': index_data,
        }
    )


@receiver(post_save, sender=DenModel)
def save_den_model_hook(sender, instance, using, **kwargs):
    layer = get_channel_layer()

    index_data = index_fetch()
    async_to_sync(layer.group_send)(
        IndexConsumer.group_name,
        {
            'type': 'update',
            'data': index_data,
        }
    )


@receiver(post_delete, sender=DenConnectionModel)
def delete_den_connection_model_hook(sender, instance, using, **kwargs):
    layer = get_channel_layer()

    index_data = index_fetch()
    async_to_sync(layer.group_send)(
        IndexConsumer.group_name,
        {
            'type': 'update',
            'data': index_data,
        }
    )


@receiver(post_save, sender=DenConnectionModel)
def save_den_connection_model_hook(sender, instance, using, **kwargs):
    layer = get_channel_layer()

    index_data = index_fetch()
    async_to_sync(layer.group_send)(
        IndexConsumer.group_name,
        {
            'type': 'update',
            'data': index_data,
        }
    )

# Adapted from https://matthiasomisore.com/uncategorized/django-delete-file-when-object-is-deleted/
@receiver(post_delete, sender=ChatMessageModel)
def delete_chat_message_model_hook(sender, instance, using, **kwargs):
    if instance.attachment:
        messages = ChatMessageModel.objects.filter(
            attachment=instance.attachment)
        if len(messages) == 0:
            instance.attachment.delete(False)

    layer = get_channel_layer()

    den_data = den_fetch(instance.den)
    async_to_sync(layer.group_send)(
        'den_%s' % instance.den.slug,
        {
            'type': 'update',
            'data': den_data,
        }
    )


@receiver(post_save, sender=ChatMessageModel)
def save_chat_message_model_hook(sender, instance, using, **kwargs):
    layer = get_channel_layer()

    den_data = den_fetch(instance.den)
    async_to_sync(layer.group_send)(
        'den_%s' % instance.den.slug,
        {
            'type': 'update',
            'data': den_data,
        }
    )


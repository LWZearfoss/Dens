from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile
from django.core.validators import validate_email, validate_slug
from django.db.models.functions import Lower
from asgiref.sync import sync_to_async
from base64 import b64decode
from datetime import datetime
from json import dumps, loads
from zlib import decompress

from .models import ChatMessageModel, DenConnectionModel, DenModel
from .validators import validate_den_name_not_empty, validate_den_name_length, validate_unique_den_name, validate_den_name_not_profane, validate_message_length, validate_message_not_profane, validateField


def den_fetch(den):
    message_objects = ChatMessageModel.objects.filter(den=den)
    data = {}
    data["den_name"] = den.name
    data["messages"] = []
    for message_object in message_objects:
        message_json = {}
        message_json["id"] = message_object.id
        message_json["text"] = message_object.text
        if message_object.attachment:
            message_json["attachment"] = message_object.attachment.url
        else:
            message_json["attachment"] = ""
        message_json["author_id"] = message_object.author.id
        message_json["author_name"] = message_object.author.username
        message_json["date"] = message_object.date.strftime(
            "%m/%d/%Y %H:%M:%S UTC")
        data["messages"] += [message_json]
    return data


class DenConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.den_slug = self.scope['url_route']['kwargs']['den_slug']
        self.den_group_name = 'den_%s' % self.den_slug
        await self.channel_layer.group_add(
            self.den_group_name,
            self.channel_name
        )

        self.den = await sync_to_async(DenModel.objects.filter)(slug=self.den_slug)
        self.den = await sync_to_async(self.den.first)()
        self.user = self.scope['user']
        self.connection = await sync_to_async(DenConnectionModel.objects.get_or_create)(user=self.user, den=self.den)
        self.connection = self.connection[0]
        self.connection.count += 1
        await sync_to_async(self.connection.save)()

        await self.accept()

        data = await sync_to_async(den_fetch)(self.den)
        await self.send(text_data=dumps({
            'data': data
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.den_group_name,
            self.channel_name
        )

        if close_code != 4000:
            self.connection.count -= 1
            await sync_to_async(self.connection.save)()
            if not self.connection.count:
                await sync_to_async(self.connection.delete)()

    async def redirect(self, event):
        data = {}
        data["redirect"] = True
        await self.send(text_data=dumps({
            'data': data
        }))
        return await self.close(4000)

    async def receive(self, text_data):
        text_data_json = loads(text_data)

        if text_data_json['create']:
            errors = []
            if not (text_data_json['text'].strip() or text_data_json['attachment'].strip()):
                errors.append("The message must be non-empty.")
            errors += await sync_to_async(validateField)(value=text_data_json['text'],
                                                         validators=[
                                                             validate_message_length,
                                                             validate_message_not_profane])
            data = {}
            data["errors"] = errors
            await self.send(text_data=dumps({
                'data': data
            }))

            if not errors:
                message_object = ChatMessageModel()
                message_object.author = self.user
                message_object.den = self.den
                message_object.text = text_data_json['text']
                # Adapted from https://stackoverflow.com/questions/39576174/save-base64-image-in-django-file-field
                if text_data_json['attachment']:
                    attachment_data = ContentFile(b64decode(decompress(b64decode(
                        text_data_json['attachment'])).decode('utf-8').split(';base64,')[1]))
                    attachment_name = text_data_json['attachment_name']
                    await sync_to_async(message_object.attachment.save)(attachment_name, attachment_data, save=False)
                await sync_to_async(message_object.save)()
        else:
            message_object = await sync_to_async(ChatMessageModel.objects.get)(pk=text_data_json["message_id"])
            await sync_to_async(message_object.delete)()

    async def update(self, event):
        data = event['data']
        await self.send(text_data=dumps({
            'data': data
        }))


def index_fetch():
    den_objects = DenModel.objects.order_by(Lower('name'))
    data = {}
    data["dens"] = []
    for den_object in den_objects:
        den = {}
        den["count"] = DenConnectionModel.objects.filter(
            den=den_object).count()
        den["id"] = den_object.id
        den["name"] = den_object.name
        den["slug"] = den_object.slug
        den["author"] = den_object.author.id
        data["dens"] += [den]
    data["dens"] = sorted(
        data["dens"], key=lambda den: den["count"], reverse=True)
    return data


class IndexConsumer(AsyncWebsocketConsumer):
    group_name = 'index'

    async def connect(self):
        self.user = self.scope['user']

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        data = await sync_to_async(index_fetch)()
        await self.send(text_data=dumps({
            'data': data
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        return await self.close()

    async def receive(self, text_data):
        text_data_json = loads(text_data)

        if text_data_json['create']:
            errors = []
            den_name = text_data_json['den_name'].strip()
            errors += await sync_to_async(validateField)(value=den_name,
                                                         validators=[validate_den_name_not_empty,
                                                                     validate_den_name_length,
                                                                     validate_unique_den_name,
                                                                     validate_den_name_not_profane])
            data = {}
            data["errors"] = errors
            await self.send(text_data=dumps({
                'data': data
            }))

            if not errors:
                den_object = DenModel()
                den_object.name = den_name
                den_object.author = self.user
                await sync_to_async(den_object.save)()
        else:
            den_object = await sync_to_async(DenModel.objects.get)(pk=text_data_json['den_id'])
            await sync_to_async(den_object.delete)()

    async def update(self, event):
        data = event['data']
        await self.send(text_data=dumps({
            'data': data
        }))

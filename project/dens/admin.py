from django.contrib import admin

from .models import ChatMessageModel, DenConnectionModel, DenModel

admin.site.register(ChatMessageModel)
admin.site.register(DenConnectionModel)
admin.site.register(DenModel)

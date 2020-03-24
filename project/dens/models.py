from django.db import models

from django.contrib.auth.models import User
from autoslug import AutoSlugField


# Adapted from https://stackoverflow.com/questions/54085690/using-django-to-dynamically-create-new-urls-pages
class DenModel(models.Model):
    name = models.CharField(max_length=24, unique=True)
    slug = AutoSlugField(populate_from='name', unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class DenConnectionModel(models.Model):
    den = models.ForeignKey(DenModel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return "Den: " + self.den.name + " User: " + self.user.username


class ChatMessageModel(models.Model):
    text = models.CharField(max_length=240, null=True)
    attachment = models.FileField(null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    den = models.ForeignKey(DenModel, on_delete=models.CASCADE)
    reply_to = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "Den: " + self.den.name + " Author: " + self.author.username + " Message: " + self.text

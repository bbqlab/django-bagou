from django.db import models


class Chat(models.Model):
    name = models.CharField(max_length=100)

import base64

from django.db import models
from django.contrib.auth import User

class TDAUser(User):
    token = models.BinaryField()

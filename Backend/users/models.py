from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class CustomUser(AbstractUser):
    username = models.CharField(max_length=20, unique=True, blank=False, null=False)
    token_invalidated = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.username}"
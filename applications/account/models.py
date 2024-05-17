import logging
import json
import datetime
import random

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone


class User(AbstractUser):
    '''
    Telegram User
    '''
    telegram_id = models.BigIntegerField(
        verbose_name='Telegram ID',
        null=True,
        blank=True,
    )

    telegram_username = models.CharField(
        max_length=100,
        blank=True,
    )

    telegram_language = models.CharField(
        max_length=16,
        default='en',
    )  # could be with dialects

    is_bot =  models.CharField(
        max_length=20,
        verbose_name='Is Bot',
        blank=True,
    )

    raw_data = models.JSONField(
        verbose_name='Raw Telegram User data',
        default=dict,
        null=True,
        blank=True,
    )

    last_number_solana_derivation_path = models.PositiveIntegerField(
        verbose_name='Last number derivation path for Solana',
        default=None,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return f"{self.username}"

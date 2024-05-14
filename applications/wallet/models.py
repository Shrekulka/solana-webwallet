from django.db import models
from django.contrib.auth import get_user_model

from applications.core.models import Common


class Wallet(Common):
    """
    Wallet
    """

    user = models.ForeignKey(
        verbose_name='Wallet owner',
        to=get_user_model(),
        on_delete=models.CASCADE,
        related_name='wallets',
    )

    name = models.CharField(
        verbose_name='Wallet name',
        max_length=100,
        blank=True,
    )

    wallet_address = models.CharField(
        verbose_name='Wallet address',
        max_length=200,
        unique=True,
    )

    description = models.CharField(
        verbose_name='Wallet description',
        max_length=200,
        blank=True,
    )

    class Meta:
        ordering = ['created']
        verbose_name = 'wallet'
        verbose_name_plural = 'wallets'

    def __str__(self):
        return self.wallet_address

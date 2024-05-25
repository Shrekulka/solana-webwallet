from django.db import models
from django.contrib.auth import get_user_model

from applications.core.models import Common


class Blockchain(models.TextChoices):
    SOLANA = 'solana', 'Solana'
    BINANCE_SMART_CHAIN = 'bsc', 'Binance Smart Chain'
    BINANCE_CHAIN = 'bnb', 'Binance Chain'
    TON = 'ton', 'Telegram Open Network'


class HDWallet(Common):
    """
    Hierarchical Deterministic wallets
    """
    user = models.ManyToManyField(
        verbose_name='HD-Wallet owners',
        to=get_user_model(),
        related_name='hdwallets',
    )

    name = models.CharField(
        verbose_name='HD-wallet name',
        max_length=100,
        blank=True,
    )

    first_address = models.CharField(
        verbose_name='First wallet address',
        help_text="Wallet address for initial derivation path, Ex.: \"m/44'/60'/0'/0/0\". Needed for identification HD-wallet",
        max_length=200,
        unique=True,
    )

    blockchain = models.CharField(
        verbose_name='Blockchain',
        choices=Blockchain.choices,
        max_length=20,
        blank=True,
    )

    last_derivation_path = models.CharField(
        verbose_name='Last derivation path',
        max_length=100,
        blank=True,
    )

    class Meta:
        ordering = ['created']
        verbose_name = 'HD-wallet'
        verbose_name_plural = 'HD-wallets'

    def __str__(self):
        return f'{self.blockchain}, {self.first_address[:4]}***{self.first_address[-4:]}'


class Wallet(Common):
    """
    Wallet
    """

    user = models.ManyToManyField(
        verbose_name='Wallet owners',
        to=get_user_model(),
        related_name='wallets',
    )

    hd_wallet = models.ForeignKey(
        verbose_name='HD-Wallet',
        to=HDWallet,
        on_delete=models.CASCADE,
        related_name='child_wallets',
        blank=True,
        null=True,
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

    blockchain = models.CharField(
        verbose_name='Blockchain',
        choices=Blockchain.choices,
        max_length=20,
        blank=True,
    )

    derivation_path = models.CharField(
        verbose_name='Derivation path',
        max_length=100,
        blank=True,
    )

    class Meta:
        ordering = ['created']
        verbose_name = 'wallet'
        verbose_name_plural = 'wallets'

    def __str__(self):
        return self.wallet_address


class Transaction(Common):
    """
    Transaction
    """
    wallet = models.ManyToManyField(
        verbose_name='Wallet',
        to=Wallet,
        related_name='transactions',
    )

    transaction_id = models.CharField(
        verbose_name='Transaction id',
        max_length=200,
        unique=True,
    )

    sender = models.CharField(
        verbose_name='Sender',
        max_length=200,
        blank=True,
    )

    recipient = models.CharField(
        verbose_name='Recipient',
        max_length=200,
        blank=True,
    )

    pre_balances = models.PositiveBigIntegerField(
        verbose_name='Pre-balances',
        blank=True,
        null=True,
    )

    post_balances = models.PositiveBigIntegerField(
        verbose_name='Post-balances',
        blank=True,
        null=True,
    )

    transaction_time = models.PositiveBigIntegerField(
        verbose_name='Transaction time',
        blank=True,
        null=True,
    )

    slot = models.PositiveBigIntegerField(
        verbose_name='Transaction slot',
        blank=True,
        null=True,
    )

    transaction_status = models.CharField(
        verbose_name='Transaction status',
        max_length=200,
        blank=True,
    )

    transaction_err = models.CharField(
        verbose_name='Transaction error',
        max_length=200,
        blank=True,
    )

    class Meta:
        ordering = ['transaction_time']
        verbose_name = 'transaction'
        verbose_name_plural = 'transactions'

    def __str__(self):
        return f'id: {self.transaction_id[:4]}...{self.transaction_id[-4:]}, time: {self.transaction_time}, slot: {self.slot}'

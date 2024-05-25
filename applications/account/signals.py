from django.db.models.signals import m2m_changed, pre_delete
from django.dispatch import receiver

from django.contrib.auth import get_user_model

User = get_user_model()


# delete related wallets
@receiver(pre_delete, sender=User)
def delete_wallet(sender, instance, **kwargs):
    wallets = instance.wallets.all()
    for wallet in wallets:
        if wallet.user.count() <= 1:
            wallet.delete()


# delete related hd-wallets
@receiver(pre_delete, sender=User)
def delete_hd_wallet(sender, instance, **kwargs):
    hd_wallets = instance.hdwallets.all()
    for hd_wallet in hd_wallets:
        if hd_wallet.user.count() <= 1:
            hd_wallet.delete()

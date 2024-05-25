from django.db.models.signals import m2m_changed, pre_delete
from django.dispatch import receiver

from applications.wallet.models import Wallet


# delete related transactions
@receiver(pre_delete, sender=Wallet)
def delete_transaction(sender, instance, **kwargs):
    transactions = instance.transactions.all()
    for tr in transactions:
        if tr.wallet.count() <= 1:
            tr.delete()

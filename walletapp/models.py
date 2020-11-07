from django.contrib.auth.models import User
from django.db import models
import uuid

TRANSACTION_TYPE = (
    (0, "Withdraw"),
    (1, "Deposit"),
)

TRANSACTION_STATUS = (
    (0, "Failed"),
    (1, "Success"),
)


class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_xid = models.OneToOneField(Customer, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True)
    balance = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    enabled_at = models.DateTimeField(auto_now=True)


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(default=0.00, max_digits=5, decimal_places=2)
    reference_id = models.UUIDField(default=uuid.uuid4, editable=False)
    txn_type = models.IntegerField(default=1, choices=TRANSACTION_TYPE)
    status = models.IntegerField(default=1, choices=TRANSACTION_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    transacted_at = models.DateTimeField(auto_now=True)

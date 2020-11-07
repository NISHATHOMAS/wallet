from rest_framework import serializers
from walletapp.models import Customer, Wallet, Transaction


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'user']


class WalletSerializer(serializers.ModelSerializer):
    owned_by = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = ['id', 'customer_xid', 'is_enabled', 'enabled_at','balance', 'owned_by']

    def get_owned_by(self, obj):
        return str(obj.customer_xid.id)

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(WalletSerializer, self).__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id']
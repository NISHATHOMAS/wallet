from rest_framework import serializers
from walletapp.models import Customer, Wallet, Transaction


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'user', 'created_at']
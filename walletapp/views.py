from django.db.models import fields
from walletapp.models import Customer, Wallet, Transaction
from walletapp.serializers import WalletSerializer, TransactionSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import (
    TokenAuthentication, )
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class ManageWallet(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    """
    Get/ Create Enable/Disable Wallet
    """
    def get(self, request, format=None):
        response_dict = {"status": "success", "data": {}}
        try:
            customer_xid = Customer.objects.get(user=request.user).id
            wallet_obj = Wallet.objects.get(customer_xid=customer_xid)
            wallet_data = WalletSerializer(wallet_obj,
                                           fields=("id", "owned_by",
                                                   "is_enabled", "enabled_at",
                                                   "balance")).data
            if wallet_data.pop("is_enabled"):
                wallet_status = "enabled"
            else:
                wallet_status = "disabled"
            response_dict["data"] = {
                "wallet": {
                    "id": wallet_data.pop("id"),
                    "owned_by": wallet_data.pop("owned_by"),
                    "status": wallet_status,
                    "disabled_at": wallet_data.pop("enabled_at"),
                    "balance": wallet_data.pop("balance")
                }
            }
        except Exception as e:
            response_dict["status"] = "failure"
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        return Response(response_dict, status=status.HTTP_200_OK)

    def patch(self, request, format=None):
        is_disabled = request.data.get("is_disabled")
        response_dict = {"status": "failure", "data": {}}
        try:
            customer_xid = Customer.objects.get(user=request.user).id
            wallet_obj = Wallet.objects.get(customer_xid=customer_xid)
            if wallet_obj.is_enabled and is_disabled:
                wallet_obj.is_enabled = False
                wallet_obj.save()
            else:
                return Response(response_dict,
                                status=status.HTTP_400_BAD_REQUEST)
            wallet_data = WalletSerializer(wallet_obj,
                                           fields=("id", "owned_by",
                                                   "is_enabled", "enabled_at",
                                                   "balance")).data
            response_dict["data"] = {
                "wallet": {
                    "id": wallet_data.pop("id"),
                    "owned_by": wallet_data.pop("owned_by"),
                    "status": "disabled",
                    "disabled_at": wallet_data.pop("enabled_at"),
                    "balance": wallet_data.pop("balance")
                }
            }
            response_dict["status"] = "success"
            return Response(response_dict, status=status.HTTP_200_OK)
        except Exception as e:
            print("ManageWallet exc: ", e)
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        print(request.user)
        response_dict = {"status": "success", "data": {}}
        customer_xid = Customer.objects.get(user=request.user).id
        try:
            wallet_obj = Wallet.objects.get(customer_xid=customer_xid)
            wallet_obj.is_enabled = True
            wallet_obj.save()
            wallet_data = WalletSerializer(wallet_obj,
                                           fields=("id", "owned_by",
                                                   "is_enabled", "enabled_at",
                                                   "balance")).data
            response_dict["data"] = {
                "wallet": {
                    "id": wallet_data.pop("id"),
                    "owned_by": wallet_data.pop("owned_by"),
                    "status": "enabled",
                    "enabled_at": wallet_data.pop("enabled_at"),
                    "balance": wallet_data.pop("balance")
                }
            }
            return Response(response_dict, status=status.HTTP_200_OK)
        except Exception as e:
            print("ManageWallet exc: ", e)
            request.data["customer_xid"] = customer_xid
            serializer = WalletSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                wallet_data = serializer.data
                response_dict["data"] = {
                    "wallet": {
                        "id": wallet_data.pop("id"),
                        "owned_by": wallet_data.pop("owned_by"),
                        "status": "enabled",
                        "enabled_at": wallet_data.pop("enabled_at"),
                        "balance": wallet_data.pop("balance")
                    }
                }
                return Response(response_dict, status=status.HTTP_201_CREATED)
            else:
                response_dict["status"] = "failure"
                print("Post Error", serializer.errors)
                return Response(response_dict,
                                status=status.HTTP_400_BAD_REQUEST)

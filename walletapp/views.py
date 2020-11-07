from django.db.models import fields
from walletapp.models import Customer, Wallet
from walletapp.serializers import WalletSerializer, TransactionSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import (
    TokenAuthentication, )
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class ManageWallet(APIView):
    """
    Get/ Create Enable/Disable Wallet
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        response_dict = {"status": "success", "data": {}}
        try:
            customer_xid = Customer.objects.get(user=request.user).id
            wallet_obj = Wallet.objects.get(customer_xid=customer_xid)
            wallet_data = WalletSerializer(wallet_obj,
                                           fields=("id", "owned_by",
                                                   "is_enabled", "enabled_at",
                                                   "balance")).data
            response_dict["data"] = {
                "wallet": {
                    "id": wallet_data.pop("id"),
                    "owned_by": wallet_data.pop("owned_by"),
                    "balance": wallet_data.pop("balance")
                }
            }
            if wallet_data.pop("is_enabled"):
                response_dict["data"]["wallet"]["status"] = "enabled"
                response_dict["data"]["wallet"][
                    "enabled_at"] = wallet_data.pop("enabled_at")
            else:
                response_dict["data"]["wallet"]["status"] = "disabled"
                response_dict["data"]["wallet"][
                    "disabled_at"] = wallet_data.pop("enabled_at")
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


class Deposit(APIView):
    """
    Deposit Money
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        response_dict = {"status": "failure", "data": {}, "msg": ""}
        try:
            wallet_obj = Wallet.objects.get(customer_xid__user=request.user)
        except Exception as e:
            print("Deposit exc: ", e)
            response_dict[
                "msg"] = "Either Wallet does not exist or Try with a different 'reference_id'"
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        request.data["wallet"] = wallet_obj.id
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            old_balance = float(wallet_obj.balance)
            new_balance = old_balance + float(serializer.data["amount"])
            wallet_obj.balance = new_balance
            wallet_obj.save()
            txn_data = serializer.data
            response_dict["data"] = {
                "deposit": {
                    "id": txn_data.pop("id"),
                    "deposited_by": wallet_obj.customer_xid.id,
                    "status": "success",
                    "deposited_at": txn_data.pop("transacted_at"),
                    "amount": serializer.data["amount"],
                    "reference_id": txn_data.pop("reference_id")
                }
            }
            response_dict["status"] = "success"
        else:
            print("Post Error", serializer.errors)
            response_dict[
                "msg"] = "Either Wallet does not exist or Try with a different 'reference_id'"
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        return Response(response_dict, status=status.HTTP_201_CREATED)


class Withdraw(APIView):
    """
    Withdraw Money
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        response_dict = {"status": "failure", "data": {}, "msg": ""}
        try:
            wallet_obj = Wallet.objects.get(
                customer_xid__user=request.user,
                balance__gte=request.data["amount"])
        except Exception as e:
            print("Deposit exc: ", e)
            response_dict[
                "msg"] = "Either Wallet/ Balance does not exist or Try with a different 'reference_id'"
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        request.data["wallet"] = wallet_obj.id
        print(request.data)
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            old_balance = float(wallet_obj.balance)
            new_balance = old_balance - float(serializer.data["amount"])
            wallet_obj.balance = new_balance
            wallet_obj.save()
            txn_data = serializer.data
            response_dict["data"] = {
                "deposit": {
                    "id": txn_data.pop("id"),
                    "withdrawn_by": wallet_obj.customer_xid.id,
                    "status": "success",
                    "withdrawn_at": txn_data.pop("transacted_at"),
                    "amount": serializer.data["amount"],
                    "reference_id": txn_data.pop("reference_id")
                }
            }
            response_dict["status"] = "success"
        else:
            print("Post Error", serializer.errors)
            response_dict[
                "msg"] = "Either Wallet/ Balance does not exist or Try with a different 'reference_id'"
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        return Response(response_dict, status=status.HTTP_201_CREATED)

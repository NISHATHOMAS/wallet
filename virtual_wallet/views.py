from __future__ import unicode_literals
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models.base import Model
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, status
from rest_framework.authtoken.models import Token
from walletapp.models import Customer
from walletapp.serializers import CustomerSerializer
from walletapp.utils import unique_string_generator


class Initialize(APIView):    
    Model = Customer
    """
    Initialize my account for wallet
    customer_xid: ea0212d3-abd6-406f-8c67-868e814a2436
    """
    def post(self, request, format=None):
        response_dict = {"status": "failure"}
        try:
            customer_obj = self.Model.objects.get(
                id=request.data["customer_xid"])
            user_obj = customer_obj.user            
        except Exception as e:
            unique = unique_string_generator()
            user_obj, yes_or_no = User.objects.get_or_create(username=unique,
                                                             password=unique)
            if not yes_or_no:
                return Response(response_dict,
                                status=status.HTTP_400_BAD_REQUEST)
        token, created = Token.objects.get_or_create(user=user_obj)
        if not created:
            token.created = timezone.now()
            token.save()
        response_dict["data"] = {"token": token.key}
        response_dict["status"] = "success"
        serializer = CustomerSerializer(data=request.data)
        request.data["user"] = user_obj.id
        request.data["id"] = request.data.pop("customer_xid")
        if serializer.is_valid():
            serializer.save()
        return Response(response_dict, status=status.HTTP_201_CREATED)

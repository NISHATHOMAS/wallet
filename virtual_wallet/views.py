from walletapp.models import Customer
from walletapp.serialzers import CustomerSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class Initialize(APIView):
    """
    Initialize my account for wallet
    customer_xid: ea0212d3-abd6-406f-8c67-868e814a2436
    """
    def post(self, request, format=None):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
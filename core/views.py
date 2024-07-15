from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from .models import Account, Destination
from .serializers import AccountSerializer, DestinationSerializer
import requests
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import JSONParser
import traceback
import secrets
import uuid


class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    @action(detail=True, methods=['get'])
    def destinations(self, request, pk=None):
        account = self.get_object()
        destinations = account.destinations.all()
        serializer = DestinationSerializer(destinations, many=True)
        return Response(serializer.data)


class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer

    def get_queryset(self):
        account_id = self.request.query_params.get('account_id', None)
        if account_id:
            return Destination.objects.filter(account__account_id=account_id)
        return super().get_queryset()


class IncomingDataView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        token = request.headers.get('CL-X-TOKEN')
        if not token:
            return Response({'error': 'Un Authenticate'}, status=status.HTTP_401_UNAUTHORIZED)

        account = get_object_or_404(Account, app_secret_token=token)
        data = request.data

        if not isinstance(data, dict):
            return Response({'error': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)

        destinations = account.destinations.all()
        for destination in destinations:
            headers = destination.headers
            url = destination.url
            method = destination.http_method.lower()

            if method == 'get':
                response = requests.get(url, headers=headers, params=data)
            else:
                response = requests.request(method, url, headers=headers, json=data)

        return Response({'status': 'Data sent to destinations'}, status=status.HTTP_200_OK)


class Accounts_Crud(APIView):

    def post(self, request):
        try:
            data = request.data
            account_details = Account.objects.create(
                email = data['email'],
                account_id = uuid.uuid1(),
                account_name = data['account_name'],
                app_secret_token = secrets.token_hex(16),
                website = data['website']
            )
            return Response({'Result' : 'The Account has been Created!'}, status=status.HTTP_200_OK)
        except Exception:
            return Response(traceback.format_exc(), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            account_details = Account.objects.filter(account_id = id).delete()
            destination_details = Destination.objects.filter(account__account_id = id).delete()
            return Response({'Result' : 'The Account has been Deleted!'}, status=status.HTTP_200_OK)
        except Exception:
            return Response(traceback.format_exc(), status=status.HTTP_400_BAD_REQUEST)


class Account_Get(APIView):

    def get(self, request, token):
        try:
            account_details = Account.objects.filter(app_secret_token = token)
            serializer = AccountSerializer(account_details, many=True)
            return Response(serializer.data)
        except Exception:
            return Response(traceback.format_exc(), status=status.HTTP_400_BAD_REQUEST)


class Destination_Crud(APIView):

    def post(self, request):
        try:
            data = request.data
            destination_details = Destination.objects.create(
                account = Account.objects.get(account_id = data['account_id']),
                url = data['url'],
                http_method = data['http_method'],
                headers = data['headers']
            )
            return Response({'Result' : 'The Destination has been Created!'}, status=status.HTTP_200_OK)
        except Exception:
            return Response(traceback.format_exc(), status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            destination_details = Destination.objects.filter(account__account_id = id).delete()
            return Response({'Result' : 'The Destination has been Deleted!'}, status=status.HTTP_200_OK)
        except Exception:
            return Response(traceback.format_exc(), status=status.HTTP_400_BAD_REQUEST)

from django.shortcuts import render
from rest_framework import generics, permissions, status
from .models import Message
from .serializers import MessageSerializer, RegisterSerializer, LoginSerializer
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.db import models
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.views import APIView

# Create your views here.

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        print("User: ",user)
        other_user_id = self.request.query_params.get('user')
        if other_user_id:
            return Message.objects.filter(
                (models.Q(sender=user) & models.Q(receiver_id=other_user_id))
                | (models.Q(sender_id=other_user_id) & models.Q(receiver=user))
            ).order_by('timestamp')
        return Message.objects.none()

    def perform_create(self, serializer):
        receiver_id = self.request.data.get('receiver')
        serializer.save(sender=self.request.user, receiver_id=receiver_id)

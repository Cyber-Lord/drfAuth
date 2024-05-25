from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated , BasePermission
from rest_framework import generics, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import UserSerializer, UserLoginSerializer
from .models import CustomUser


class HelloView(APIView):
    permission_classes = (IsAuthenticated,)           

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)
    
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key})
            else:
                return Response({'error': 'Invalid credentials'}, status=401)
        else:
            return Response(serializer.errors, status=400)

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class EditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        # Ensure object exists
        try:
            instance = CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'Object not found'}, status=404)

        # Validate and save the data
        serializer = UserSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        
        # Handle validation errors
        return JsonResponse(serializer.errors, status=400)

class EditProfileView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsOwner]

    def update(self, request, *args, **kwargs):
        # Only the owner can update their profile.
        pass
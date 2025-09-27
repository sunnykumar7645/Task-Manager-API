from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from taskapi.serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, UserChangePasswordSerializer, SendPasswordResetEmailSerializer, UserPasswordResetSerializer
from django.contrib.auth import authenticate
from taskapi.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .models import Task
from .serializers import TaskSerializer
from .pagination import TaskPagination

# Generate token manually

def get_tokens_for_user(user):
    # if not user.is_active:
    #   raise AuthenticationFailed("User is not active")
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }




# Create your views here.

class UserRegistrationView(APIView):
    renderer_classes=[UserRenderer]
    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token= get_tokens_for_user(user)
            return Response({"message":"User registered sucessfully...", "token":token}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    renderer_classes=[UserRenderer]
    def post(self, request, format=None):
        serializer =UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                return Response({"message":"User Logged in sucessfully...", "token":token}, status=status.HTTP_200_OK)
            else:
                return Response({"Errors":{'non_field_errors':'email and password do not match'}}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
    

class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({"message":"Password changed sucessfully..."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
    
class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]
    # permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({"message":"Password reset link send, Please check you email."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data = request.data, context={'uid':uid, 'token' : token})
        if serializer.is_valid(raise_exception=True):
            return Response({"message":"Password reset succesfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)






class TaskListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # GET /tasks?completed=true 
    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response({"detail": "Please login first"}, status=status.HTTP_401_UNAUTHORIZED)

        # Get tasks for the logged-in user
        tasks = Task.objects.filter(user=request.user).order_by('-created_at')

        # Filtering by completed status
        completed_param = request.query_params.get('completed')
        if completed_param is not None:
            if completed_param.lower() in ['true', '1']:
                tasks = tasks.filter(completed=True)
            elif completed_param.lower() in ['false', '0']:
                tasks = tasks.filter(completed=False)

        # Apply pagination
        paginator = TaskPagination()
        paginated_tasks = paginator.paginate_queryset(tasks, request, view=self)

        # If paginator applied
        if paginated_tasks is not None:
            serializer = TaskSerializer(paginated_tasks, many=True)
            return paginator.get_paginated_response(serializer.data)

        # If pagination not applied, return all
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    # POST /tasks  Create new task
    def post(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response({"detail": "Please login first"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class TaskDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # helper method  ensures only owner can access
    def get_object(self, pk, user):
        return get_object_or_404(Task, pk=pk, user=user)

    # GET /tasks/{id}  Retrieve single task
    def get(self, request, pk):
        task = self.get_object(pk, request.user)
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    

    # PUT /tasks/{id}  Full update (all fields required)
    def put(self, request, pk):
        task = self.get_object(pk, request.user)
        serializer = TaskSerializer(task, data=request.data)  # overwrite all fields
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH /tasks/{id}  Partial update (only some fields)
    def patch(self, request, pk):
        task = self.get_object(pk, request.user)
        serializer = TaskSerializer(task, data=request.data, partial=True)  # allow partial updates
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE /tasks/{id}  Delete a task
    def delete(self, request, pk):
        if not request.user or not request.user.is_authenticated:
            return Response({"detail": "Please login first"}, status=status.HTTP_401_UNAUTHORIZED)

        task = self.get_object(pk, request.user)
        task.delete()
        return Response({"message": "Task deleted successfully"}, status=status.HTTP_200_OK)
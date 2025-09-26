from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
import random
from .mail import MailUtils
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from rest_framework import generics, permissions
from rest_framework.decorators import action




# Create your views here.

def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        return {
            # 'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

def generate_otp():
    # Generate a 6-digit OTP
    return random.randint(100000, 999999)

"""User register api"""
class UserRegistrationAPIView(APIView):
    def post(self, request):
        data = request.data
        serializer = UserRegistrationSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save(is_active=True)
            
            return Response({
                "message": "User Registered Successfully",
                "user_id": user.id,
                "email": user.email
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


######################################  USER LOGIN ######################################################

class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']



        # user = authenticate(email=email, password=password)
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({'error': 'Invalid email or password'}, status=400)


        # Generate tokens
        token = get_tokens_for_user(user)
        user_data = UserLoginFieldsSerializer(user).data
        user_data['access_token'] = token['access']

        return Response({
            'code': '200',
            'message': 'Login Successfully',
            'data': user_data
        }, status=status.HTTP_200_OK)


########################################### USER'S QUESTIONS #############################################

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.prefetch_related("options").all()
    serializer_class = QuestionSerializer


#################################### QUESTION ANSWERS API  ##################################################

class SubmitAnswersAPIView(APIView):

    def post(self, request):
        user_id = request.data.get('user_id')
        answers_data = request.data.get('answers')

        if not user_id or not answers_data:
            return Response({"error": "user_id and answers are required"}, status=status.HTTP_400_BAD_REQUEST)

        created_answers = []
        for ans in answers_data:
            serializer = AnswerSerializer(data={
                "user_id": user_id,
                "question_id": ans['question_id'],
                "option_id": ans['option_id']
            })
            if serializer.is_valid():
                serializer.save()
                created_answers.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Answers saved successfully", "answers": created_answers}, status=status.HTTP_201_CREATED)


############################################# PASSWORD RESET ############################################

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # send email
        MailUtils.send_password_reset_email(user)

        return Response({"detail": "Password reset link has been sent to your email."}, status=status.HTTP_200_OK)
    

class PasswordResetConfirmView(APIView):
    def post(self, request, uid, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid_decoded = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uid_decoded)
        except (TypeError, ValueError, User.DoesNotExist):
            return Response({"detail": "Invalid UID"}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        # hash new password
        new_password = serializer.validated_data["new_password"]
        user.password = make_password(new_password)
        user.save()

        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)


######################################### CREATE POST AND COMMENT ########################################

class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Retrieve, Update, Delete
class PostRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only allow actions on posts owned by the logged-in user
        return Post.objects.filter(user=self.request.user)

# Like a post
class PostLikeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = Post.objects.get(pk=pk)
        user = request.user

        if user in post.dislikes.all():
            post.dislikes.remove(user)

        if user in post.likes.all():
            post.likes.remove(user)  # toggle
        else:
            post.likes.add(user)

        return Response({"likes": post.likes.count(), "dislikes": post.dislikes.count()})

# Dislike a post
class PostDislikeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        post = Post.objects.get(pk=pk)
        user = request.user

        if user in post.likes.all():
            post.likes.remove(user)

        if user in post.dislikes.all():
            post.dislikes.remove(user)  
        else:
            post.dislikes.add(user)

        return Response({"likes": post.likes.count(), "dislikes": post.dislikes.count()})
    

# Comment on a post
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Comment.objects.all()

    def perform_create(self, serializer):
        # Automatically assign user
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        post_id = self.request.query_params.get('post_id')
        if post_id:
            # Return only top-level comments (parent=None) for this post
            queryset = queryset.filter(post_id=post_id, parent=None).order_by('-created_at')
        return queryset

    # Optional: get replies for a specific comment
    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        comment = self.get_object()
        serializer = self.get_serializer(comment.replies.all(), many=True)
        return Response(serializer.data)
    

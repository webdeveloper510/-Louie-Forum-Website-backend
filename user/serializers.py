from .models import *
from rest_framework import serializers
from django.contrib.auth.hashers import make_password




class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','email','password','verified_otp']

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    


class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate_email(self, value):
        return value.lower()
    

class UserLoginFieldsSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id','email']




class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text']


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'options']


class AnswerSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user')
    question_id = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all(), source='question')
    option_id = serializers.PrimaryKeyRelatedField(queryset=Option.objects.all(), source='option')

    class Meta:
        model = Answer
        fields = ['user_id', 'question_id', 'option_id']



class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password does not match."})
        return attrs
    

class PostSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField() 

    class Meta:
        model = Post
        fields = [
            "id", "user", "title", "content", "image", 
            "created_at", "likes_count", "dislikes_count","comment_count"
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_dislikes_count(self, obj):
        return obj.dislikes.count()
    
    def get_comment_count(self, obj):
        return obj.comments.count()
    

class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'content', 'parent', 'replies', 'created_at']
        read_only_fields = ['user', 'replies', 'created_at']

    def get_replies(self, obj):
        return CommentSerializer(obj.replies.all(), many=True).data
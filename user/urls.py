from django.urls import path
from .views import *
from django.urls import include
from rest_framework.routers import DefaultRouter



router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationAPIView.as_view(), name="register"),
    path('login/', UserLoginView.as_view(), name='login'),
    path('submit-answers/', SubmitAnswersAPIView.as_view(), name='submit-answers'),
    path("reset-password-request/", PasswordResetRequestView.as_view(), name="reset-password-request"),
    path("reset-password/<uid>/<token>/", PasswordResetConfirmView.as_view(), name="reset-password-confirm"),
    path("posts/", PostListCreateView.as_view(), name="posts-list-create"),
    path("posts/<int:pk>/", PostRetrieveUpdateDestroyView.as_view(), name="post-detail"),
    path("posts/<int:pk>/like/", PostLikeAPIView.as_view(), name="post-like"),
    path("posts/<int:pk>/dislike/", PostDislikeAPIView.as_view(), name="post-dislike"),
]+ router.urls
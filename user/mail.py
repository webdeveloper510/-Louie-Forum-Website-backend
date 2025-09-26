from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes


class MailUtils:
    @staticmethod
    def send_password_reset_email(user):
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)

        # reset_link = f"http://localhost:3000/new-password?uid={uid}&token={token}"
        reset_link = f"http://localhost:8000/api/reset-password/{uid}/{token}/"
        print("reset link", reset_link)


        subject = "Password Reset Email - Arise Court"
        html_message = render_to_string("email_verification_template/password_reset.html", {
            'user': user,
            'reset_link': reset_link,
        })

        send_mail(
            subject=subject,
            message=html_message,  
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
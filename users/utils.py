# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_str
# from django.contrib.auth.tokens import default_token_generator
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.conf import settings

# def send_activation_email(user, request):
#     uid = urlsafe_base64_encode(force_bytes(user.pk))
#     token = default_token_generator.make_token(user)
#     activate_url = request.build_absolute_uri(f"/api/users/activate/{uid}/{token}/")
#     subject = "Activate your account"
#     context = {"user": user, "activate_url": activate_url}
#     text = render_to_string("activate.txt", context)
#     html = render_to_string("activate.html", context) if hasattr(settings, "TEMPLATES") else None
#     send_mail(subject, text, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html)


# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.contrib.auth.tokens import default_token_generator
# from django.core.mail import send_mail
# from django.template.loader import render_to_string
# from django.conf import settings
# from django.urls import reverse


# def send_activation_email(user, request):
#     # Make sure the user is saved before generating uid/token
#     uid = urlsafe_base64_encode(force_bytes(user.pk))
#     token = default_token_generator.make_token(user)

#     # Build URL using reverse()
#     activate_url = request.build_absolute_uri(
#         reverse("activate", kwargs={"uidb64": uid, "token": token})
#     )

#     subject = "Activate your account"
#     context = {"user": user, "activate_url": activate_url}

#     text = render_to_string("activate.txt", context)
#     html = render_to_string("activate.html", context)

#     send_mail(
#         subject,
#         text,
#         settings.DEFAULT_FROM_EMAIL,
#         [user.email],
#         html_message=html,
#     )

from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self,user,timestamp):
        return (six.text_type(user.pk)+six.text_type(timestamp)+six.text_type(user.is_active))
generate_token=TokenGenerator()


from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer, ProfileSerializer
from .jwt_serializers import MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.shortcuts import get_object_or_404
# from .utils import send_activation_email
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Profile
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
# -----------------------------
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail

# for sending mails and generate token
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from .utils import generate_token
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives

#email active
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.views.generic import View

User = get_user_model()

# class RegisterAPIView(generics.CreateAPIView):
#     serializer_class = RegisterSerializer
#     permission_classes = [AllowAny]

#     def perform_create(self, serializer):
#         user = serializer.save()
#         # send activation email (if email provided)
#         request = self.request
#         if user.email:
#             send_activation_email(user, request)

#     def create(self, request, *args, **kwargs):
#         resp = super().create(request, *args, **kwargs)
#         return Response({"detail": "Account created. Check email to activate."}, status=status.HTTP_201_CREATED)

def get_tokens_for_user(user):
    refresh=RefreshToken.for_user(user)
    return{
        'refresh':str(refresh),
        'access':str(refresh.access_token)
    }


class RegisterAPIView(APIView):
    serializer_class=RegisterSerializer
    
    def post(self,request):
        serializer=self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user=serializer.save()
            tokens=get_tokens_for_user(user)
            
            
            email_subject="Activate Your Account"
            message=render_to_string(
                'activate.html',
            {
                'user':user,
                'domain':'http://127.0.0.1:8000',
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':generate_token.make_token(user),
                # 'jwt':tokens
            }

            )
            email_message=EmailMultiAlternatives(email_subject,message,to=[user.email])
            email_message.attach_alternative(message,"text/html")
            email_message.send()
            return Response("Check your mail for confirmation.") 
            
            # return Response({
            #     "User Name":user.username,
            #     "First Name":user.first_name,
            #     "Last Name":user.last_name,
            #     "Email":user.email,
            #     "tokens":tokens,
            # },status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors)


# class ActivateAPIView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request, uidb64, token):
#         try:
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(pk=uid)
#         except Exception:
#             return Response({"detail": "Invalid activation link."}, status=status.HTTP_400_BAD_REQUEST)

#         if default_token_generator.check_token(user, token):
#             user.is_active = True
#             user.save()
#             return Response({"detail": "Account activated."}, status=status.HTTP_200_OK)
#         return Response({"detail": "Activation link invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)


class ActivateAPIView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            return redirect('register')
        else:
            return redirect('register') 



# JWT views
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# TokenRefreshView available from simplejwt

# Logout: blacklist refresh token
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Expect body: {"refresh": "<refresh_token>"}
        """
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail":"Refresh token required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # requires token_blacklist app and migrations
            return Response({"detail":"Logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail":"Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


# Profile viewset (simple)
class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # User only sees their own profile
        return Profile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Prevent multiple profiles per user
        if Profile.objects.filter(user=self.request.user).exists():
            raise ValidationError("You already have a profile.")
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        # Return the single profile instead of a list
        profile = get_object_or_404(Profile, user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        # Always fetch the user’s own profile
        profile = get_object_or_404(Profile, user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        # Update user’s profile
        profile = get_object_or_404(Profile, user=request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        # Partially update profile
        profile = get_object_or_404(Profile, user=request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        # Delete user’s profile
        profile = get_object_or_404(Profile, user=request.user)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



# --------------------

class PasswordResetRequestAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail":"Email required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # do not reveal whether email exists
            return Response({"detail":"If that email exists, a reset email has been sent."})
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = request.build_absolute_uri(f"/api/users/password-reset-confirm/{uid}/{token}/")
        # send email (render templates as you prefer)
        send_mail("Password reset", f"Reset here: {reset_url}", None, [user.email])
        return Response({"detail":"If that email exists, a reset email has been sent."})

class PasswordResetConfirmAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"detail":"Invalid link."}, status=status.HTTP_400_BAD_REQUEST)
        if not default_token_generator.check_token(user, token):
            return Response({"detail":"Invalid or expired link."}, status=status.HTTP_400_BAD_REQUEST)
        password = request.data.get("password")
        if not password or len(password) < 8:
            return Response({"detail":"Password must be at least 8 chars."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.save()
        return Response({"detail":"Password has been reset."}, status=status.HTTP_200_OK)



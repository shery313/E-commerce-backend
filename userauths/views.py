from django.shortcuts import render
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from store.models import CartOrder

# Restframework
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken

# Others
import json
import random

# Serializers
from userauths.serializer import MyTokenObtainPairSerializer, ProfileSerializer, RegisterSerializer, UserSerializer


# Models
from userauths.models import Profile, User


# This code defines a DRF View class called MyTokenObtainPairView, which inherits from TokenObtainPairView.
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Normalize email before processing login
        normalized_email = request.data.get('email', '').lower()
        request.data['email'] = normalized_email
        
        # Call the parent class's post method to handle the token logic
        response = super().post(request, *args, **kwargs)

        # After successful authentication, fetch the user based on the email
        user = User.objects.filter(email=normalized_email).first()

        if user:
            # Filter CartOrder by email and assign it to the logged-in user
            CartOrder.objects.filter(email=normalized_email).update(buyer=user)

        return response


# This code defines another DRF View class called RegisterView, which inherits from generics.CreateAPIView.
from datetime import timedelta
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        normalized_email = serializer.validated_data.get('email', '').lower()
        user = serializer.save(email=normalized_email)
        user.is_active = False  # Deactivate account till it is confirmed
        user.otp = generate_numeric_otp()
        user.otp_expiry = timezone.now() + timedelta(minutes=5)
        uidb64 = user.pk
        token = default_token_generator.make_token(user)
        user.reset_token = token
        user.save()

        # Filter CartOrder by email and assign to the newly created user
        CartOrder.objects.filter(email=normalized_email).update(buyer=user)

        # Send email verification
        link = f"https://localhost:3000/email-verify?uidb64={uidb64}&token={token}&otp={user.otp}"
        

        merge_data = {
                'username': user.username,
                'otp': user.otp,
                'link':link,
                'current_year': timezone.now().year
                }
        subject = "Email Verification"
        text_body = render_to_string("email/verification_email.txt", merge_data)
        html_body = render_to_string("email/verification_email.html", merge_data)
        msg = EmailMultiAlternatives(subject, text_body, settings.EMAIL_HOST_USER, [user.email])
        msg.attach_alternative(html_body, "text/html")
        msg.send()


class VerifyEmail(generics.CreateAPIView):
    permission_classes=[AllowAny,]
    serializer_class=UserSerializer
    
    def create(self,request,*args, **kwargs):

        try:
            uidb64 = request.data.get('uidb64')
            token = request.data.get('token')
            otp = request.data.get('otp')
            print(uidb64,token,otp)
            user = User.objects.get(pk=uidb64,otp=otp,reset_token=token)
            print(user)
            

            if user:
                user.is_active = True
                # user.email_verified = True
                user.otp = ""
                user.reset_token=""
                user.save()
                return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid token or OTP'}, status=status.HTTP_400_BAD_REQUEST)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)



# This is a DRF view defined as a Python function using the @api_view decorator.
@api_view(['GET'])
def getRoutes(request):
    # It defines a list of API routes that can be accessed.
    routes = [
        '/api/token/',
        '/api/register/',
        '/api/token/refresh/',
        '/api/test/'
    ]
    # It returns a DRF Response object containing the list of routes.
    return Response(routes)

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

class VerifyOTPView(APIView):
    def post(self, request, *args, **kwargs):
        otp = request.data.get('otp')
        user = User.objects.filter(otp=otp).first()

        if user and user.otp_expiry > timezone.now():
            user.is_active = True
            user.otp = None  # Clear OTP after successful verification
            user.otp_expiry = None
            user.save()
            return Response({'success': True, 'message': 'Email verified successfully'})
        return Response({'success': False, 'message': 'Invalid or expired OTP'})
class ResendOtpView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('uidb64')
        try:
            user = User.objects.get(user=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if user.is_active:
            return Response({'message': 'Email is already verified.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.otp = generate_numeric_otp()
        user.otp_expiry = timezone.now() + timezone.timedelta(minutes=5)  # OTP expires in 5 minutes
        user.save()
        
        # Send OTP email
        # link = f"https://vivifystore.netlify.app/verify-email?uidb64={urlsafe_base64_encode(force_bytes(user.pk))}&otp={user.otp}"
        merge_data = {'otp': user.otp, 'username': user.username}
        subject = "Email Verification OTP"
        text_body = render_to_string("email/otp_email.txt", merge_data)
        html_body = render_to_string("email/otp_email.html", merge_data)
        msg = EmailMultiAlternatives(subject, text_body, settings.EMAIL_HOST_USER, [user.email])
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        
        return Response({'message': 'OTP has been resent.'}, status=status.HTTP_200_OK)


# This is another DRF view defined as a Python function using the @api_view decorator.
# It is decorated with the @permission_classes decorator specifying that only authenticated users can access this view.
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def testEndPoint(request):
    # Check if the HTTP request method is GET.
    if request.method == 'GET':
        # If it is a GET request, it constructs a response message including the username.
        data = f"Congratulations {request.user}, your API just responded to a GET request."
        # It returns a DRF Response object with the response data and an HTTP status code of 200 (OK).
        return Response({'response': data}, status=status.HTTP_200_OK)
    # Check if the HTTP request method is POST.
    elif request.method == 'POST':
        try:
            # If it's a POST request, it attempts to decode the request body from UTF-8 and load it as JSON.
            body = request.body.decode('utf-8')
            data = json.loads(body)
            # Check if the 'text' key exists in the JSON data.
            if 'text' not in data:
                # If 'text' is not present, it returns a response with an error message and an HTTP status of 400 (Bad Request).
                return Response("Invalid JSON data", status=status.HTTP_400_BAD_REQUEST)
            text = data.get('text')
            # If 'text' exists, it constructs a response message including the received text.
            data = f'Congratulations, your API just responded to a POST request with text: {text}'
            # It returns a DRF Response object with the response data and an HTTP status code of 200 (OK).
            return Response({'response': data}, status=status.HTTP_200_OK)
        except json.JSONDecodeError:
            # If there's an error decoding the JSON data, it returns a response with an error message and an HTTP status of 400 (Bad Request).
            return Response("Invalid JSON data", status=status.HTTP_400_BAD_REQUEST)
    # If the request method is neither GET nor POST, it returns a response with an error message and an HTTP status of 400 (Bad Request).
    return Response("Invalid JSON data", status=status.HTTP_400_BAD_REQUEST)


# This code defines another DRF View class called ProfileView, which inherits from generics.RetrieveAPIView and used to show user profile view.
class ProfileView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProfileSerializer

    def get_object(self):
        user_id = self.kwargs['user_id']

        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)
        return profile
    

def generate_numeric_otp(length=7):
        # Generate a random 7-digit OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
        return otp

class PasswordEmailVerify(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer
    
    def get_object(self):
        email = self.kwargs['email']
        user = User.objects.get(email=email)
        
        if user:
            user.otp = generate_numeric_otp()
            uidb64 = user.pk
            
             # Generate a token and include it in the reset link sent via email
            refresh = RefreshToken.for_user(user)
            reset_token = str(refresh.access_token)

            # Store the reset_token in the user model for later verification
            user.reset_token = reset_token
            user.save()

            link = f"http://localhost:5173/create-new-password?otp={user.otp}&uidb64={uidb64}&reset_token={reset_token}"
            
            merge_data = {
                'link': link, 
                'username': user.username, 
            }
            subject = f"Password Reset Request"
            text_body = render_to_string("email/password_reset.txt", merge_data)
            html_body = render_to_string("email/password_reset.html", merge_data)
            
            msg = EmailMultiAlternatives(
                subject=subject, from_email=settings.FROM_EMAIL,
                to=[user.email], body=text_body
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send()
        return user
    

class PasswordChangeView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer
    
    def create(self, request, *args, **kwargs):
        payload = request.data
        
        otp = payload['otp']
        uidb64 = payload['uidb64']
        reset_token = payload['reset_token']
        password = payload['password']

        print("otp ======", otp)
        print("uidb64 ======", uidb64)
        print("reset_token ======", reset_token)
        print("password ======", password)

        user = User.objects.get(id=uidb64, otp=otp)
        if user:
            user.set_password(password)
            user.otp = ""
            user.reset_token = ""
            user.save()

            
            return Response( {"message": "Password Changed Successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response( {"message": "An Error Occured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

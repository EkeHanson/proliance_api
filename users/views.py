from rest_framework import viewsets, status, generics
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import UserRegistrationSerializer, LoginSerializer, SendOTPSerializer, VerifyOTPSerializer,ChangePasswordSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated
import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView
from rest_framework.views import APIView
import logging

logger = logging.getLogger(__name__)

class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            
            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SendOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']

        try:
            user = CustomUser.objects.get(phone=phone_number)
        except ObjectDoesNotExist:
            return Response({'detail': 'User with this phone number does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        otp_value = '123456'  # Replace with a method to generate a dynamic OTP
        otp_template_name = 'OTP_Template_Name'  # Replace with your actual template name

        url = f'https://2factor.in/API/V1/{settings.TWO_FACTOR_API_KEY}/SMS/{phone_number}/{otp_value}/{otp_template_name}'
        response = requests.get(url)

        if response.status_code == 200:
            otp_session_id = response.json().get('Details')
            return Response({'message': 'OTP sent successfully', 'otp_session_id': otp_session_id}, status=status.HTTP_200_OK)
        return Response({'detail': 'Failed to send OTP'}, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_session_id = serializer.validated_data['otp_session_id']
        otp_entered_by_user = serializer.validated_data['otp_entered_by_user']

        url = f'https://2factor.in/API/V1/{settings.TWO_FACTOR_API_KEY}/SMS/VERIFY/{otp_session_id}/{otp_entered_by_user}'
        response = requests.get(url)

        if response.status_code == 200 and response.json().get('Details') == 'OTP Matched':
            return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = UserRegistrationSerializer

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # Disable authentication for this view

    def post(self, request):
        logger.debug(f"Login request received with data: {request.data}")
        logger.debug(f"Request headers: {request.headers}")

        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            logger.debug("Missing email or password")
            return Response(
                {'detail': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=email, password=password)
        logger.debug(f"Authentication result: {user}")

        if user is not None:
            refresh = RefreshToken.for_user(user)
            logger.debug("User authenticated successfully")
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'userId': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_type': user.user_type,
                'date_joined': user.date_joined,
            }, status=status.HTTP_200_OK)
        else:
            logger.debug("Authentication failed: Invalid credentials")
            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

@api_view(['POST'])
@permission_classes([AllowAny])
def send_contact_email(request):
    if request.method == 'POST':
        email = request.data.get('email')
        full_name = request.data.get('full_name')
        phone_number = request.data.get('phone_number')
        interest_service = request.data.get('interest_service')
        message_body = request.data.get('message')

        if not email:
            return Response({'error': 'Email is required'}, status=400)

        subject = 'Contact Form Submission'
        html_message = f'''
        <html>
        <body>
            <h3>Contact Form Submission</h3>
            <p><strong>Full Name:</strong> {full_name or 'N/A'}</p>
            <p><strong>Email Address:</strong> {email}</p>
            <p><strong>Phone Number:</strong> {phone_number or 'N/A'}</p>
            <p><strong>Interest Service:</strong> {interest_service or 'N/A'}</p>
            <p><strong>Message:</strong> {message_body or 'N/A'}</p>
        </body>
        </html>
        '''
        plain_message = f"""
        Contact Form Submission
        Full Name: {full_name or 'N/A'}
        Email Address: {email}
        Phone Number: {phone_number or 'N/A'}
        Interest Service: {interest_service or 'N/A'}
        Message: {message_body or 'N/A'}
        """
        recipient_list = ['info@artstraining.co.uk', 'support@artstraining.co.uk', 'ekenhanson@gmail.com', 'Diana@adada.co.uk']
        from_email = 'admin@artstraining.co.uk'

        try:
            send_mail(
                subject,
                plain_message,
                from_email,
                recipient_list,
                fail_silently=False,
                html_message=html_message
            )
            return Response({'message': 'Email sent successfully'})
        except Exception as e:
            return Response({'error': f'Failed to send email: {str(e)}'}, status=500)
    else:
        return Response({'error': 'Invalid request method'}, status=400)
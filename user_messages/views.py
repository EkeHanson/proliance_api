from .models import ContactMessage
from .serializers import ContactMessageSerializer
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from rest_framework.response import Response


class ContactMessageView(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = ContactMessage.objects.all().order_by('-created_at')
    serializer_class = ContactMessageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Save the message if data is valid
            contact_message = serializer.save()

            # Send an email after the message is successfully created
            email = contact_message.email
            full_name = contact_message.name
            phone_number = contact_message.phone
            interest_service = contact_message.service_of_interest
            message_body = contact_message.message


            subject = 'Contact Form Submission'
            message = f'''
            <html>
            <body>
                <h3>Contact Form Submission</h3>
                <p><strong>Full Name:</strong> {full_name}</p>
                <p><strong>Email Address:</strong> {email}</p>
                <p><strong>Phone Number:</strong> {phone_number}</p>
                <p><strong>Interest Service:</strong> {interest_service}</p>
                <p><strong>Message:</strong> {message_body}</p>
            </body>
            </html>
            '''
            recipient_list = ['info@prolianceltd.com']
            from_email = 'prolianzltd@gmail.com'

            # Send the email with HTML content
            send_mail(
                subject,
                '',
                from_email,
                recipient_list,
                fail_silently=False,
                html_message=message
            )

            return Response({'message': 'Message sent successfully'}, status=status.HTTP_201_CREATED)
        
        else:
            # Print and return detailed serializer errors
            # print("serializer.errors")
            # print(serializer.errors)
            # print("serializer.errors")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

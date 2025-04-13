from .models import ContactMessage
from .serializers import ContactMessageSerializer
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from rest_framework.response import Response
from .models import QuoteRequest
from .serializers import QuoteRequestSerializer
from datetime import datetime
from django.conf import settings
from .models import DemoRequest
from .serializers import DemoRequestSerializer

from rest_framework.pagination import PageNumberPagination
from rest_framework import generics

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
import os

@csrf_exempt
def get_ga_data(request):
    # Path to your service account JSON key
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    credentials_path = os.path.join(BASE_DIR, 'user_messages', 'google_json_key.json')
    
    # Initialize GA4 client
    client = BetaAnalyticsDataClient.from_service_account_file(credentials_path)
    
    # Example: Fetch most visited pages (modify as needed)
    request = RunReportRequest(
        property=f"properties/381575215",  # Replace with your GA4 property ID
        dimensions=[Dimension(name="pageTitle"), Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews")],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
    )
    
    response = client.run_report(request)
    
    # Format data for React
    data = []
    for row in response.rows:
        data.append({
            "page_title": row.dimension_values[0].value,
            "page_path": row.dimension_values[1].value,
            "views": row.metric_values[0].value,
        })
    
    return JsonResponse({"data": data})


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# Contact Message Views
class ContactMessageListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = ContactMessage.objects.all().order_by('created_at')
    serializer_class = ContactMessageSerializer
    pagination_class = StandardResultsSetPagination

class ContactMessageDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    lookup_field = 'id'

# Quote Request Views
class QuoteRequestListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = QuoteRequest.objects.all().order_by('created_at')
    serializer_class = QuoteRequestSerializer
    pagination_class = StandardResultsSetPagination

class QuoteRequestDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = QuoteRequest.objects.all()
    serializer_class = QuoteRequestSerializer
    lookup_field = 'id'

# Demo Request Views
class DemoRequestListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = DemoRequest.objects.all().order_by('created_at')
    serializer_class = DemoRequestSerializer
    pagination_class = StandardResultsSetPagination

class DemoRequestDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = DemoRequest.objects.all()
    serializer_class = DemoRequestSerializer
    lookup_field = 'id'

class DemoRequestView(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = DemoRequest.objects.all().order_by('created_at')
    serializer_class = DemoRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Save the demo request if data is valid
            demo_request = serializer.save()

            # Send confirmation email to the requester
            self.send_confirmation_email(demo_request)
            
            # Send notification email to your team
            self.send_notification_email(demo_request)

            return Response({'message': 'Demo request submitted successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_confirmation_email(self, demo_request):
        subject = 'Your Demo Request Has Been Received'
        html_message = f'''
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Demo Request Confirmation</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: Poppins, sans-serif; font-size: 15px; font-weight: 400; line-height: 1.5; width: 100%; background: #081C15; color: #fff; overflow-x: hidden; min-height: 100vh; text-align: center;">
            <div style="position: relative; width: 100%; height: auto; min-height: 100%; display: flex; justify-content: center;">
                <div style="position: relative; width: 700px; height: auto; text-align: center; padding: 80px 0px; padding-bottom: 0px !important;">
                    <img src="https://prolianceltd.com/assets/anim-logo1-C0x_JQ1e.png" style="max-width: 150px; margin-bottom: 80px;" />
                    <h3 style="font-size: 30px; font-weight: 700;">Thank you, {demo_request.first_name}!</h3>

                    <p style="margin-top: 10px; color:#D8F3DC;">We've received your request for a demo and our team will get back to you shortly to schedule a session.</p>
                    
                    <div style="text-align: left; margin: 30px auto; max-width: 500px; padding: 20px; background-color: rgba(255,255,255,0.1); border-radius: 8px;">
                        <h4 style="color: #FE6601; margin-bottom: 15px;">Request Details:</h4>
                        <p><strong>Name:</strong> {demo_request.first_name} {demo_request.last_name}</p>
                        <p><strong>Company:</strong> {demo_request.company_name}</p>
                        <p><strong>Email:</strong> {demo_request.email}</p>
                        <p><strong>Country:</strong> {demo_request.country}</p>
                        <p><strong>Phone:</strong> {demo_request.phone_number}</p>
                        <p><strong>Message:</strong> {demo_request.message}</p>
                    </div>

                    <footer style="position: relative; width: 100%; height: auto; margin-top: 50px; padding: 30px; background-color: rgba(255,255,255,0.1);">
                        <h5>Thank you for your interest in our products</h5>
                        <p style="font-size: 13px !important; color: #fff !important;">You can reach us via <a href="mailto:support@cmvp.net" style="color:#D8F3DC !important; text-decoration: underline !important;">support@cmvp.net</a>. We are always available to answer your questions.</p>
                        <p style="font-size: 13px !important; color: #fff !important;">© {datetime.now().year} CMVP. All rights reserved.</p>
                    </footer>
                </div>
            </div>
        </body>
        </html>
        '''
        
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [demo_request.email]

        send_mail(
            subject,
            '',
            from_email,
            recipient_list,
            fail_silently=False,
            html_message=html_message
        )

    def send_notification_email(self, demo_request):
        subject = f'New Demo Request from {demo_request.company_name}'
        html_message = f'''
        <html>
        <body>
            <h3>New Demo Request Received</h3>
            <p><strong>Name:</strong> {demo_request.first_name} {demo_request.last_name}</p>
            <p><strong>Company:</strong> {demo_request.company_name}</p>
            <p><strong>Email:</strong> {demo_request.email}</p>
            <p><strong>Phone:</strong> {demo_request.phone_number}</p>
            <p><strong>Country:</strong> {demo_request.country}</p>
            <p><strong>Message:</strong> {demo_request.message}</p>
            <p><strong>Submitted on:</strong> {demo_request.created_at.strftime('%Y-%m-%d %H:%M')}</p>
        </body>
        </html>
        '''
        
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = ['ekenehanson@gmail.com', 'ekehanson@gmail.com']
        # recipient_list = ['support@prolianceltd.com', 'info@prolianceltd.com']

        send_mail(
            subject,
            '',
            from_email,
            recipient_list,
            fail_silently=False,
            html_message=html_message
        )


class QuoteRequestView(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = QuoteRequest.objects.all().order_by('created_at')
    serializer_class = QuoteRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Save the quote request if data is valid
            quote_request = serializer.save()

            # Send confirmation email to the requester
            #self.send_confirmation_email(quote_request)
            
            # Send notification email to your team
            self.send_notification_email(quote_request)

            return Response({'message': 'Quote request submitted successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_confirmation_email(self, quote_request):
        subject = 'Your Quote Request Has Been Received'
        html_message = f'''
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Quote Request Confirmation</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: Poppins, sans-serif; font-size: 15px; font-weight: 400; line-height: 1.5; width: 100%; background: #081C15; color: #fff; overflow-x: hidden; min-height: 100vh; text-align: center;">
            <div style="position: relative; width: 100%; height: auto; min-height: 100%; display: flex; justify-content: center;">
                <div style="position: relative; width: 700px; height: auto; text-align: center; padding: 80px 0px; padding-bottom: 0px !important;">
                    <img src="https://prolianceltd.com/assets/anim-logo1-C0x_JQ1e.png" style="max-width: 150px; margin-bottom: 80px;" />
                    <h3 style="font-size: 30px; font-weight: 700;">Thank you, {quote_request.first_name}!</h3>

                    <p style="margin-top: 10px; color:#D8F3DC;">We've received your request for a quote and our team will get back to you shortly.</p>
                    
                    <div style="text-align: left; margin: 30px auto; max-width: 500px; padding: 20px; background-color: rgba(255,255,255,0.1); border-radius: 8px;">
                        <h4 style="color: #FE6601; margin-bottom: 15px;">Request Details:</h4>
                        <p><strong>Name:</strong> {quote_request.first_name} {quote_request.last_name}</p>
                        <p><strong>Company:</strong> {quote_request.company_name}</p>
                        <p><strong>Email:</strong> {quote_request.email}</p>
                        <p><strong>Country:</strong> {quote_request.country}</p>
                        <p><strong>Phone:</strong> {quote_request.phone_number}</p>
                        <p><strong>Message:</strong> {quote_request.message}</p>
                    </div>

                    <footer style="position: relative; width: 100%; height: auto; margin-top: 50px; padding: 30px; background-color: rgba(255,255,255,0.1);">
                        <h5>Thank you for considering our services</h5>
                        <p style="font-size: 13px !important; color: #fff !important;">You can reach us via <a href="mailto:support@cmvp.net" style="color:#D8F3DC !important; text-decoration: underline !important;">support@cmvp.net</a>. We are always available to answer your questions.</p>
                        <p style="font-size: 13px !important; color: #fff !important;">© {datetime.now().year} CMVP. All rights reserved.</p>
                    </footer>
                </div>
            </div>
        </body>
        </html>
        '''
        
        from_email = settings.DEFAULT_FROM_EMAIL  # Replace with your sender email
        recipient_list =  [quote_request.email]

        send_mail(
            subject,
            '',
            from_email,
            recipient_list,
            fail_silently=False,
            html_message=html_message
        )


    def send_notification_email(self, quote_request):
        subject = f'New Quote Request from {quote_request.company_name}'
        html_message = f'''
        <html>
        <body>
            <h3>New Quote Request Received</h3>
            <p><strong>Name:</strong> {quote_request.first_name} {quote_request.last_name}</p>
            <p><strong>Company:</strong> {quote_request.company_name}</p>
            <p><strong>Email:</strong> {quote_request.email}</p>
            <p><strong>Phone:</strong> {quote_request.phone_number}</p>
            <p><strong>Country:</strong> {quote_request.country}</p>
            <p><strong>Message:</strong> {quote_request.message}</p>
            <p><strong>Submitted on:</strong> {quote_request.created_at.strftime('%Y-%m-%d %H:%M')}</p>
        </body>
        </html>
        '''
        
        from_email = settings.DEFAULT_FROM_EMAIL  # Replace with your sender email
        recipient_list =  ['ekenehanson@gmail.com', 'ekehanson@gmail.com']
        # recipient_list =  ['support@prolianceltd.com', 'info@prolianceltd.com']

        send_mail(
            subject,
            '',
            from_email,
            recipient_list,
            fail_silently=False,
            html_message=html_message
        )
        print("Email Sent")
    

class ContactMessageView(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = ContactMessage.objects.all().order_by('created_at')
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
            from_email = settings.DEFAULT_FROM_EMAIL  # Replace with your sender email
            recipient_list =  ['ekenehanson@gmail.com', 'ekehanson@gmail.com']    
           # recipient_list =  ['support@prolianceltd.com', 'info@prolianceltd.com']]
        

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

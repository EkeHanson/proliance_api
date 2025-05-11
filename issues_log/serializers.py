# serializers.py
from rest_framework import serializers
from .models import Category, Issue, Comment, Notification
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
  
class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    mentioned_users = serializers.ListField(
        child=serializers.EmailField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Comment
        fields = ['id', 'issue', 'author', 'text', 'timestamp', 'mentioned_users']
        read_only_fields = ['issue', 'author', 'timestamp']  # Make 'issue' read-only

    def create(self, validated_data):
        mentioned_emails = validated_data.pop('mentioned_users', [])
        comment = super().create(validated_data)
        
        # Log mentioned emails for debugging
        print(f"Creating comment with mentioned emails: {mentioned_emails}")
        
        # Create notifications in bulk
        notifications = []
        for email in mentioned_emails:
            try:
                user = User.objects.get(email=email)
                notifications.append(
                    Notification(
                        recipient=user,
                        issue=comment.issue,
                        comment=comment
                    )
                )
            except User.DoesNotExist:
                print(f"User with email {email} does not exist")
                continue
        
        Notification.objects.bulk_create(notifications)
        print(f"Created {len(notifications)} notifications")
        
        # Send emails to mentioned users
        for notification in notifications:
            issue_url = f"http://127.0.0.1:9090/api/issues_log/issues/{comment.issue.id}"
            subject = f"You were mentioned in a comment on Issue {comment.issue.id}"
            message = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Issue Comment Mention Notification</title>
            </head>
            <body style="margin: 0; padding: 0; font-family: Poppins, sans-serif; font-size: 15px; font-weight: 400; line-height: 1.5; width: 100%; background: #081C15; color: #fff; overflow-x: hidden; min-height: 100vh; text-align: center;">
                <div style="position: relative; width: 100%; height: auto; min-height: 100%; display: flex; justify-content: center;">
                    <div style="position: relative; width: 700px; height: auto; text-align: center; padding: 80px 0px; padding-bottom: 0px !important;">
                        <img src="https://cmvp.net/assets/logo-lit-Cz1jHCfU.png" style="max-width: 150px; margin-bottom: 80px;" />
                        <h3 style="font-size: 30px; font-weight: 700;">Mention in Comment</h3>
                        <p style="margin-top: 10px; color:#D8F3DC;">
                            You were mentioned in a comment on issue <strong>{comment.issue.id}: {comment.issue.title}</strong> by {comment.author.email}.
                        </p>
                        <p style="margin-top: 20px; color:#D8F3DC;">
                            Comment: {comment.text}
                        </p>
                        <a href="{issue_url}" style="display: inline-block; margin-top: 30px; padding: 10px 20px; background: #FE6601; color: #fff; text-decoration: none; border-radius: 5px;">
                            View Issue
                        </a>
                        <footer style="position: relative; width: 100%; height: auto; margin-top: 50px; padding: 30px; background-color: rgba(255,255,255,0.1);">
                            <h5>Thank you for using our platform</h5>
                            <p style="font-size: 13px !important; color: #fff !important;">
                                You can reach us via <a href="mailto:support@cmvp.net" style="color:#D8F3DC !important; text-decoration: underline !important;">support@cmvp.net</a>.
                                We are always available to answer your questions.
                            </p>
                            <p style="font-size: 13px !important; color: #fff !important;">
                                © <script>document.write(new Date().getFullYear());</script> CMVP. All rights reserved.
                            </p>
                        </footer>
                    </div>
                </div>
            </body>
            </html>
            """
            try:
                print(f"Sending email to {notification.recipient.email}")
                send_mail(
                    subject,
                    '',
                    settings.DEFAULT_FROM_EMAIL,
                    [notification.recipient.email],
                    fail_silently=False,
                    html_message=message,
                )
                print(f"Email sent to {notification.recipient.email}")
            except Exception as e:
                print(f"Failed to send email to {notification.recipient.email}: {str(e)}")
                raise
                
        return comment

class NotificationSerializer(serializers.ModelSerializer):
    issue = serializers.CharField(source='issue.id')
    comment = CommentSerializer()
    
    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'issue', 'comment', 'read', 'created_at']

class IssueSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Issue
        fields = '__all__'

    def update(self, instance, validated_data):
        if 'status' in validated_data:
            new_status = validated_data['status']
            if new_status in ['Resolved', 'Closed'] and not instance.date_resolved:
                instance.date_resolved = timezone.now().date()
            elif new_status in ['Open', 'In Progress'] and instance.date_resolved:
                instance.date_resolved = None
        return super().update(instance, validated_data)

class IssueCreateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    assigned_to = serializers.CharField(allow_null=True, required=False)
    reported_by = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = Issue
        fields = '__all__'
        read_only_fields = ['id', 'date_reported', 'created_at', 'updated_at']

class IssueStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['status']
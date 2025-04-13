# models.py

from django.db import models

class ContactMessage(models.Model):
    SERVICE_CHOICES = [
        ('Consultancy', 'Consultancy'),
        ('Engineering', 'Engineering'),
        ('Project Management', 'Project Management'),
        ('Supply Chain Management', 'Supply Chain Management'),
        ('Learning and Development', 'Learning and Development'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    service_of_interest = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"


class DemoRequest(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    company_name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Demo request from {self.first_name} {self.last_name} ({self.company_name})"

class QuoteRequest(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    company_name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} from {self.company_name}"
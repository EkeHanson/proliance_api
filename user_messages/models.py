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

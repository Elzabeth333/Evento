from django.db import models
from django.contrib.auth.models import User
import random
from adminpanel.models import Events
from datetime import timedelta
from django.utils import timezone
import uuid




class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def has_expired(self):
        expiration_time = self.created_at + timedelta(minutes=10)
        return timezone.now() > expiration_time

    def save(self, *args, **kwargs):
        if not self.otp_code:
            self.otp_code = str(random.randint(100000, 999999))  # Generate 6-digit OTP
        super(OTP, self).save(*args, **kwargs)

    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp_code}"
    



class Blog(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    event = models.ForeignKey(Events, on_delete=models.SET_NULL, null=True, blank=True)  # Optional event association
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)

    def __str__(self):
        return self.title
    



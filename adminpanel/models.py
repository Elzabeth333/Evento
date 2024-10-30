from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum
import uuid
from django.conf import settings
from django.utils import timezone



class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company')
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    profile_image = models.ImageField(upload_to='company/profile_pics/', null=True, blank=True)
    id_proof = models.CharField(max_length=50, null=False, blank=False)
    id_proof_image = models.ImageField(upload_to='company/images/', null=True, blank=True)
    pan_number = models.CharField(max_length=20, null=False, blank=False)
    gst_number = models.CharField(max_length=20, null=False, blank=False)
    is_active = models.BooleanField(default=False)  # Add this field to track activation status
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Profile of {self.user.username}'

# Attendee model
class Attendee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    profile_image = models.ImageField(upload_to='attendee/profile_pics/', null=True, blank=True)
    id_proof = models.CharField(max_length=50, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    attended = models.BooleanField(default=False)

    def __str__(self):
        return f'Profile of {self.user.username}'
       

#Not used Event model




class Events(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    event_image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    time = models.TimeField(null=False, blank=False)
    location = models.ForeignKey('Venue', on_delete=models.CASCADE)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  # Example
    # completion_date = models.DateTimeField(null=True , blank= True)

    def __str__(self):
        return self.title

    @property
    def seats_available(self):
        """Calculate the number of available seats dynamically."""
        # Assuming the location.capacity represents the total seats for this event.
        booked_seats = BookNoww.objects.filter(event=self).aggregate(total_seats=Sum('number_of_seats'))['total_seats'] or 0
        return self.location.capacity - booked_seats

    def reduce_seats(self, number_of_seats):
        """Reduce the number of available seats by a given amount."""
        booked_seats = BookNoww.objects.filter(event=self).aggregate(total_seats=Sum('number_of_seats'))['total_seats'] or 0
        available_seats = self.location.capacity - booked_seats
        
        if available_seats >= number_of_seats:
            # Proceed with the booking
            return True
        else:
            # Not enough seats available
            return False
        



class Venue(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()
    venue_image = models.ImageField(upload_to='venue_images/', null=True, blank=True)

    def __str__(self):
        return self.name
    



class TicketType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name







class BookNoww(models.Model):
    TICKET_TYPE_CHOICES = [
        ('starter', 'Starter'),
        ('standard', 'Standard'),
        ('platinum', 'Platinum'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Events, related_name='bookings', on_delete=models.CASCADE)  # Added related_name='bookings'
    ticket_type = models.CharField(max_length=10, choices=TICKET_TYPE_CHOICES)
    number_of_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    is_cancelled = models.BooleanField(default=False)
    booking_serial = models.UUIDField(default=uuid.uuid4, editable=False)  # Unique serial number for each booking
    booking_date = models.DateTimeField(default=timezone.now)



    def clean(self):
        if self.number_of_seats > self.available_seats:
            raise ValidationError("Number of seats booked cannot exceed available seats.")

    def save(self, *args, **kwargs):
    # Calculate ticket price based on type
        base_price = self.event.ticket_price
        if self.ticket_type == 'starter':
            self.ticket_price = base_price
        elif self.ticket_type == 'standard':
            self.ticket_price = base_price * 2
        elif self.ticket_type == 'platinum':
            self.ticket_price = base_price * 3

    # Correct the super() call
        super(BookNoww, self).save(*args, **kwargs)



    def __str__(self):
        return f"{self.event.title} - {self.ticket_type} - {self.user.username} - Serial: {self.booking_serial}"














class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.user.username}: {self.message}'
 
    
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # Add this field if it's missing
    is_deleted = models.BooleanField(default=False)  # New field to track if a message is deleted
    deleted_at = models.DateTimeField(null=True, blank=True)  # New field to store when a message is deleted

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'
# models.py

from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

class Location(models.Model):
    name = models.CharField(max_length=100)
    # Add other fields as needed

    def __str__(self):
        return self.name

class RoomType(models.Model):
    name = models.CharField(max_length=100)
    # Add other fields as needed

    def __str__(self):
        return self.name
class Hotels(models.Model):
    name = models.CharField(max_length=30, default="BY")
    owner = models.CharField(max_length=20)
    location = models.CharField(max_length=50)
    state = models.CharField(max_length=50, default="Hyderabad")
    country = models.CharField(max_length=50, default="India")

    def __str__(self):
        return self.name

    def calculate_price(self, location, room_type, check_in, check_out):
        # Example logic to calculate price based on location, room_type, check_in, check_out
        # Replace with your actual pricing logic based on your application's requirements
        price = 0  # Placeholder value, replace with actual logic
        
        # Example: Calculate price based on room type and duration of stay
        if location == self.location:  # Simplified check for location
            room = self.rooms.filter(room_type=room_type).first()
            if room:
                # Example: Calculate price based on room's price and duration of stay
                price = room.price * ((check_out - check_in).days + 1)
        
        return price

class Rooms(models.Model):
    ROOM_STATUS = ( 
        ("1", "available"), 
        ("2", "not available"),    
    ) 

    ROOM_TYPE = ( 
        ("1", "premium"), 
        ("2", "deluxe"),
        ("3", "basic"),    
    ) 

    room_type = models.CharField(max_length=50, choices=ROOM_TYPE)
    capacity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.IntegerField()
    hotel = models.ForeignKey(Hotels, related_name='rooms', on_delete=models.CASCADE)
    status = models.CharField(choices=ROOM_STATUS, max_length=15)
    roomnumber = models.IntegerField()

    def __str__(self):
        return f"{self.room_type} Room in {self.hotel.name}"

class Reservation(models.Model):
    check_in = models.DateField()
    check_out = models.DateField()
    room = models.ForeignKey(Rooms, on_delete=models.CASCADE, related_name='reservations')
    guest = models.ForeignKey(User, on_delete=models.CASCADE)
    booking_id = models.CharField(max_length=100, default="null")

    def __str__(self):
        return f"Reservation #{self.id} - {self.guest.username}"
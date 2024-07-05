from django.shortcuts import render ,redirect, get_object_or_404, HttpResponse
from django.http import HttpResponse , HttpResponseRedirect
from .models import Hotels,Rooms,Reservation, Location
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import datetime
#from datetime import datetime
from .forms import BookingForm
# Create your views here.

def homepage(request):
    # Your logic for homepage view
    return render(request, 'index.html')
def reviewpage(request):
    return HttpResponse(render(request,'reviews.html'))
def contactpage(request):
    return HttpResponse(render(request,'contact.html'))
def aboutpage(request):
    return HttpResponse(render(request,'about.html'))
def user_homepage(request):
    all_location = Hotels.objects.values_list('location', 'id').distinct().order_by()
    
    if request.method == "POST":
        try:
            print(request.POST)
            hotel = Hotels.objects.get(id=int(request.POST['search_location']))
            rr = []
            
            # Find reserved rooms for excluding from query set
            for each_reservation in Reservation.objects.all():
                date_string_checkin = request.POST['cin']
                date_string_checkout = request.POST['cout']
                checkin_data = datetime.strptime(date_string_checkin, '%Y-%m-%d')
                checkout_data = datetime.strptime(date_string_checkout, '%Y-%m-%d')
                if each_reservation.check_in < checkin_data.date() and each_reservation.check_out < checkout_data.date():
                    pass
                elif each_reservation.check_in > checkin_data.date() and each_reservation.check_out > checkout_data.date():
                    pass
                else:
                    rr.append(each_reservation.room.id)
                
            rooms = Rooms.objects.filter(hotel=hotel, capacity__gte=int(request.POST['capacity'])).exclude(id__in=rr)
            
            if len(rooms) == 0:
                messages.warning(request, "Sorry, no rooms are available during this time period.")
            
            data = {'rooms': rooms, 'all_location': all_location, 'flag': True}
            response = render(request, 'index.html', data)
        
        except Exception as e:
            messages.error(request, str(e))
            response = render(request, 'index.html', {'all_location': all_location})
    
    else:
        data = {'all_location': all_location}
        response = render(request, 'index.html', data)
    
    return HttpResponse(response)

# Staff homepage
def staff_homepage(request):
    all_location = Hotels.objects.values_list('location', 'id').distinct().order_by()
    data = {'all_location': all_location}
    response = render(request, 'index.html', data)
    return HttpResponse(response)

    
#user sign up
def user_sign_up(request):
    if request.method =="POST":
        user_name = request.POST['username']
        
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.warning(request,"Password didn't matched")
            return redirect('userloginpage')
        
        try:
            if User.objects.all().get(username=user_name):
                messages.warning(request,"Username Not Available")
                return redirect('userloginpage')
        except:
            pass
            

        new_user = User.objects.create_user(username=user_name,password=password1)
        new_user.is_superuser=False
        new_user.is_staff=False
        new_user.save()
        messages.success(request,"Registration Successfull")
        return redirect("userloginpage")
    return render(request,'user/userlogsign.html')
#staff sign up
def staff_sign_up(request):
    if request.method =="POST":
        user_name = request.POST['username']
        
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.success(request,"Password didn't Matched")
            return redirect('staffloginpage')
        try:
            if User.objects.all().get(username=user_name):
                messages.warning(request,"Username Already Exist")
                return redirect("staffloginpage")
        except:
            pass
        
        new_user = User.objects.create_user(username=user_name,password=password1)
        new_user.is_superuser=False
        new_user.is_staff=True
        new_user.save()
        messages.success(request," Staff Registration Successfull")
        return redirect("staffloginpage")
    else:

        return render(request,'user/userlogsign.html')
#user login and signup page
def user_log_sign_page(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['pswd']

        user = authenticate(username=email, password=password)

        if user is not None and not user.is_staff:  # Check if user is not staff
            login(request, user)
            messages.success(request, "Successfully logged in")
            return redirect('homepage')
        else:
            messages.error(request, "Incorrect username or password")
            return redirect('userloginpage')

    return render(request, 'user/userlogsign.html')

#logout for admin and user 
def logoutuser(request):
    if request.method == 'GET' and request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out successfully")
        return redirect('homepage')
    else:
        messages.error(request, "Logout unsuccessful")
        return redirect('userloginpage')

#staff login and signup page
def staff_log_sign_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('staffpanel')
        else:
            messages.error(request, "Incorrect username or password")
            return redirect('staffloginpage')

    return render(request, 'staff/stafflogsign.html')

# staff panel page
@login_required(login_url='/staff')
def panel(request):
    
    if request.user.is_staff == False:
        return HttpResponse('Access Denied')
    
    rooms = Rooms.objects.all()
    total_rooms = len(rooms)
    available_rooms = len(Rooms.objects.all().filter(status='1'))
    unavailable_rooms = len(Rooms.objects.all().filter(status='2'))
    reserved = len(Reservation.objects.all())

    hotel = Hotels.objects.values_list('location','id').distinct().order_by()
    print(hotel)

    response = render(request,'staff/panel.html',{'location':hotel,'reserved':reserved,'rooms':rooms,'total_rooms':total_rooms,'available':available_rooms,'unavailable':unavailable_rooms})
    return HttpResponse(response)

#for editing room information
@login_required(login_url='/staff')
def edit_room(request):
    if request.user.is_staff == False:   
        return HttpResponse('Access Denied')
    if request.method == 'POST' and request.user.is_staff:
        print(request.POST)
        old_room = Rooms.objects.all().get(id= int(request.POST['roomid']))
        hotel = Hotels.objects.all().get(id=int(request.POST['hotel']))
        old_room.room_type  = request.POST['roomtype']
        old_room.capacity   =int(request.POST['capacity'])
        old_room.price      = float(request.POST['price'])
        old_room.size       = int(request.POST['size'])
        old_room.hotel      = hotel
        old_room.status     = request.POST['status']
        old_room.room_number=int(request.POST['roomnumber'])

        old_room.save()
        messages.success(request,"Room Details Updated Successfully")
        return redirect('staffpanel')
    else:
    
        room_id = request.GET['roomid']
        room = Rooms.objects.all().get(id=room_id)
        response = render(request,'staff/editroom.html',{'room':room})
        return HttpResponse(response)

#for adding room
@login_required(login_url='/staff')
def add_new_room(request):
    if request.user.is_staff == False:
        return HttpResponse('Access Denied')
    if request.method == "POST":
        total_rooms = len(Rooms.objects.all())
        new_room = Rooms()
        hotel = Hotels.objects.all().get(id = int(request.POST['hotel']))
        print(f"id={hotel.id}")
        print(f"name={hotel.name}")


        new_room.roomnumber = total_rooms + 1
        new_room.room_type  = request.POST['roomtype']
        new_room.capacity   = int(request.POST['capacity'])
        new_room.size       = int(request.POST['size'])
        new_room.capacity   = int(request.POST['capacity'])
        new_room.hotel      = hotel
        new_room.status     = request.POST['status']
        new_room.price      = request.POST['price']

        new_room.save()
        messages.success(request,"New Room Added Successfully")
    
    return redirect('staffpanel')

#booking room page
@login_required(login_url='/user')
def book_room_page(request):
    room_id = request.GET.get('roomid')
    if not room_id:
        # Handle case where 'roomid' is not found in request.GET
        # For example, redirect with an error message or render an error page
        return HttpResponse("Room ID is required for booking.")
    
    room = get_object_or_404(Rooms, id=room_id)
    # Assuming 'Rooms' is the correct model name for rooms in your app
    
    return render(request, 'user/bookroom.html', {'room': room})

@login_required(login_url='/user')  # Ensure user is logged in to access this view
def book_room(request):
    if request.method == "POST":
        room_id = request.POST.get('room_id')
        check_in = datetime.datetime.strptime(request.POST.get('check_in'), '%Y-%m-%d').date()
        check_out = datetime.datetime.strptime(request.POST.get('check_out'), '%Y-%m-%d').date()
        total_person = int(request.POST.get('person'))

        try:
            room = Rooms.objects.get(id=room_id)
        except Rooms.DoesNotExist:
            messages.error(request, "Selected room does not exist.")
            return redirect("userhomepage")

        # Check if room is available for booking
        reservations = Reservation.objects.filter(room=room)
        for each_reservation in reservations:
            if check_in < each_reservation.check_out and check_out > each_reservation.check_in:
                messages.warning(request, "Sorry, this room is unavailable for booking during this period.")
                return redirect("userhomepage")

        # Create reservation if room is available
        room.status = '2'  # Update room status to booked
        room.save()

        current_user = request.user
        user_object = User.objects.get(username=current_user)

        reservation = Reservation.objects.create(
            guest=user_object,
            room=room,
            check_in=check_in,
            check_out=check_out,
        )
        reservation.save()

        messages.success(request, "Congratulations! Booking successful.")
        return redirect("userhomepage")
    else:
        return HttpResponse('Access Denied')

def handler404(request, exception):
    return render(request, '404.html', status=404)
 
@login_required(login_url='/staff')   
def view_room(request):
    room_id = request.GET['roomid']
    room = Rooms.objects.all().get(id=room_id)

    reservation = Reservation.objects.all().filter(room=room)
    return HttpResponse(render(request,'staff/viewroom.html',{'room':room,'reservations':reservation}))

@login_required(login_url='/userloginpage')
def user_bookings(request):
    if request.user.is_authenticated == False:
        return redirect('userloginpage')
    user = User.objects.all().get(id=request.user.id)
    print(f"request user id ={request.user.id}")
    bookings = Reservation.objects.all().filter(guest=user)
    if not bookings:
        messages.warning(request,"No Bookings Found")
    return HttpResponse(render(request,'user/mybookings.html',{'bookings':bookings}))

@login_required(login_url='/staff')
def add_new_location(request):
    if request.method == "POST" and request.user.is_staff:
        owner = request.POST['new_owner']
        location = request.POST['new_city']
        state = request.POST['new_state']
        country = request.POST['new_country']
        
        hotels = Hotels.objects.all().filter(location = location , state = state)
        if hotels:
            messages.warning(request,"Sorry City at this Location already exist")
            return redirect("staffpanel")
        else:
            new_hotel = Hotels()
            new_hotel.owner = owner
            new_hotel.location = location
            new_hotel.state = state
            new_hotel.country = country
            new_hotel.save()
        messages.success(request,"New Location Has been Added Successfully")
    return redirect("staffpanel")

    # else:
    #     return HttpResponse("Not Allowed")
    
#for showing all bookings to staff
@login_required(login_url='/staff')
def all_bookings(request):
   
    bookings = Reservation.objects.all()
    if not bookings:
        messages.warning(request,"No Bookings Found")
    return HttpResponse(render(request,'staff/allbookings.html',{'bookings':bookings}))
    


        
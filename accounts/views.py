from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import random
from .forms import CustomUserCreationForm
from .models import CustomUser

def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False
                user.otp = generate_otp()
                user.otp_created_at = timezone.now()
                user.save()
                
                # Send OTP email with better formatting
                email_subject = 'Verify your Campus Carpool account'
                email_message = f'''
                Hello {user.username},

                Your OTP for email verification is: {user.otp}

                This OTP will expire in 10 minutes.

                Best regards,
                Campus Carpool Team
                '''
                
                send_mail(
                    email_subject,
                    email_message,
                    'shivasounshi143@gmail.com',  # Make sure this matches your EMAIL_HOST_USER
                    [user.email],
                    fail_silently=False,
                )
                
                request.session['registration_user_id'] = user.id
                messages.success(request, 'Registration successful! Please check your email for OTP.')
                return redirect('verify_otp')
            except Exception as e:
                messages.error(request, f'Error sending email: {str(e)}')
                user.delete()  # Clean up if email fails
                return redirect('register')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def verify_otp(request):
    user_id = request.session.get('registration_user_id')
    if not user_id:
        messages.error(request, 'Registration session expired.')
        return redirect('register')
    
    user = CustomUser.objects.get(id=user_id)
    
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if user.otp == otp:
            # Check if OTP is still valid (10 minutes)
            if timezone.now() - user.otp_created_at <= timedelta(minutes=10):
                user.is_active = True
                user.email_verified = True
                user.otp = None
                user.save()
                login(request, user)
                messages.success(request, 'Email verified successfully!')
                return redirect('ride_list')
            else:
                messages.error(request, 'OTP expired. Please register again.')
                user.delete()
                return redirect('register')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    
    return render(request, 'accounts/verify_otp.html')

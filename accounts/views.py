from django.shortcuts import redirect, render
from .models import User,UserProfile
from .forms import UserForm
from django.contrib import messages,auth
from vendor.forms import VendorForm
from .utils import detectUser,send_email_verification
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from vendor.models import Vendor
# Create your views here.

def registerUser(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.set_password(password)
            user.role= user.CUSTOMER
            form.save()
            
            #send verification email
            mail_subject='Please activate your account'
            email_template='accounts/emails/account_verification_email.html'
            send_email_verification(request,user,mail_subject,email_template) 
            
            messages.success(request,"User has been created successfully!")

            #can also use create_user method
            #first_name=form.cleaned_data['first_name']
            #... 重复步骤
            #user=User.objects.create_user(first_name = first_name)
            #user.role=user.CUSTOMER
            #user.save()
            print('user is saved')
            return redirect('registerUser')
    else:
        form = UserForm()
    
    context = {
        'form':form 
    }
    return render(request,'accounts/registerUser.html',context)


def registerVendor(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST,request.FILES)
        
        if form.is_valid() and  v_form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
            user.role = user.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user=user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            #send verification email
            mail_subject='Please activate your account'
            email_template='accounts/emails/reset_password_email.html'
            send_email_verification(request,user,mail_subject,email_template)  
            
            messages.success(request,'Your account has been registered successfully!')
            return redirect('registerVendor')
        else:
            print('invalid form')
            print(form.errors,v_form.errors)
        
        
    else:
        form = UserForm()
        v_form = VendorForm()
    context = {
        'form':form,
        'v_form':v_form
    }
    
    return render(request,'accounts/registerVendor.html',context)

def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Congrats, your account is activated')
        return redirect('myAccount')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('myAccount')
    
def login(request):
    if request.user.is_authenticated:
        messages.warning(request,"You are already logged in!")
        return redirect('myAccount')
    if request.method == 'POST':
            print(request.POST,request.method)
            email = request.POST['email']
            password = request.POST['password']
            user = auth.authenticate(email=email,password=password)
            if user is not None:
                auth.login(request,user)
                messages.success(request,'You are now logged in')
                return redirect('myAccount')
            else:
                messages.error(request,"invalid login")
                return redirect('login')
    return render(request,'accounts/login.html')

    
def logout(request):
    auth.logout(request)
    messages.info(request,'you are logged out')
    return redirect('login')

@login_required(login_url='login')
def myAccount(request):
    user = request.user #这是哪里来的
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url='login')
def custDashboard(request):
    return render(request,'accounts/custDashboard.html')


@login_required(login_url='login')
def vendorDashboard(request):
    vendor = Vendor.objects.get(user=request.user)
 
    return render(request,'accounts/vendorDashboard.html')


def forgot_password(request):
    if request.method == 'POST':
        email =request.POST['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)
            
            #send reset password email
            mail_subject = 'Please reset your password'
            email_template='accounts/emails/reset_password_email.html'
            send_email_verification(request,user,mail_subject,email_template)
            
            messages.success(request,'Password reset link has been sent to your email address.')
            
            return redirect('login')
        else:
            messages.error(request,'Account does not exist')
            return redirect('forgot_password')
         
    return render(request,'accounts/forgot_password.html')


def reset_password_validate(request,uidb64,token):
    #user click the link, sending a request with pk and token
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid 
        messages.info(request,'please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request,'Invalid link')
        return redirect('myAccount')
     

def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            pk=request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True 
            user.save()
            messages.success(request,'Password reset successfully')
            return redirect('login')
        else:
            messages.error(request,'password does not match')
            return redirect('reset_password')
        
    return render(request,'accounts/reset_password.html')
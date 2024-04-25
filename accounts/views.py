from django.shortcuts import redirect, render
from .models import User,UserProfile
from .forms import UserForm
from django.contrib import messages,auth
from vendor.forms import VendorForm
from .utils import detectUser
from django.contrib.auth.decorators import login_required

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

def login(request):
    if request.user.is_authenticated:
        messages.warning(request,"You are already logged in!")
        return redirect('myAccount')
    if request.method == 'POST':
            print(request.POST)
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
    return render(request,'accounts/vendorDashboard.html')

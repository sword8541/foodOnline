from django.shortcuts import redirect, render
from .models import User
from .forms import UserForm

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
            
            #can also use create_user method
            #first_name=form.cleaned_data['first_name']
            #... 重复步骤
            #user=User.objects.create_user(first_name = first_name)
            #user.role=user.CUSTOMER
            #user.save()
            print('user is saved')
            return render(request,'accounts/success.html')
        else:
            print('invalid form')
            print(form.errors)
    else:
        form = UserForm()
    
    context = {
        'form':form 
    }
    return render(request,'accounts/registerUser.html',context)
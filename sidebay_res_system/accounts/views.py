from django.shortcuts import render
from django.contrib.auth import authenticate
from accounts.models import User

def top(request):
    return render(request, 'app/registration/login.html', {})

def main(request):
        user = User.objects.filter(mail_address=request.POST.get("mail_address", "")).first()

        if user is not None:
            if user.check_pass(request.POST.get("password", "")):
                return render(request, 'app/registration/main.html')
            else:
                return render(request, 'app/registration/login.html',
                              {"error": "Your account has been disablede!"})
        else:
            return render(request, 'app/registration/login.html', {"error": "Your username and password were not available!!"})


def lottery(request):
    pass

def login(request):
    pass


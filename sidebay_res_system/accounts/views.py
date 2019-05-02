from django.shortcuts import render
from django.contrib.auth import authenticate

def top(request):
    return render(request, 'app/registration/login.html', {})

def main(request):
        user = authenticate(username=request.POST.get("username", ""), password=request.POST.get("password", ""))

        if user is not None:
            if user.is_active:
                print("You provided a correct username and password!")
            else:
                return render(request, 'app/registration/login.html',
                              {"error": "Your account has been disablede!"})

        else:
            return render(request, 'app/registration/login.html', {"error": "Your username and password were not available!!"})

        return render(request, 'app/registration/main.html')

def lottery(request):
    pass

def login(request):
    pass


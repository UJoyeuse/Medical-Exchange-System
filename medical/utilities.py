from django.core.exceptions import PermissionDenied
import re
from django.shortcuts import redirect
from .models import Medicine
from .models import Hospital


def check_if_manager(function):
    def wrap(request, *args, **kwargs):
        try:
            hospital = Hospital.objects.get(leader=request.user)

        except:
            return redirect('login')
        if hospital.approved is False:
            return redirect('wait')
        return function(request, *args, **kwargs)
    return wrap


def redirect_user(user):
    hospitals = Hospital.objects.filter(leader=user)
    if hospitals.exists():

        return "DASHBOARD"
    elif user.is_superuser:
        return "ADMIN"
    else:
        return redirect('login')


def check_strong_password(password):
    if len(password) <= 7:
        return {"code": False, "message": "Password should contain at least 7 characters."}
    else:
        for char in '!@#$$%^&*()_+':
            if char in password:
                for pass_character in password:
                    if pass_character.isupper():
                        for car_digit in password:
                            if car_digit.isdigit():
                                return {"code": True}
                            else:
                                pass
                        return {"code": False, "message": "Password should contain at least one digit."}
                    else:
                        pass

                return {"code": False, "message": "Password should at least have one uppercased character."}
            else:
                pass

        return {"code": False, "message": "Password should contain at least one special character."}



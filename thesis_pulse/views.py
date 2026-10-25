from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from apps.authentication.models import PasswordResetRequest

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        
        user = authenticate(request, username=identifier, password=password)
        
        
        if user is None:
            user_obj = User.objects.filter(email__iexact=identifier).first()
            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Bon retour, {user.first_name or user.username} !")

            
            if user.is_superuser or getattr(user, 'role', '') == 'ADMIN':
                return redirect('scheduling:admin_dashboard')
            elif getattr(user, 'role', '') in ['SUPERVISOR', 'JURY'] or getattr(user, 'is_jury_member', False):
                return redirect('ai_module:supervisor_dashboard')
            else:
                return redirect('academic:student_dashboard')
        else:
            messages.error(request, "Email ou mot de passe incorrect.")
            return redirect('login')

    return render(request, 'authentication/login.html')


def forgot_password_view(request):
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            user_obj = User.objects.filter(email__iexact=email).first()
            PasswordResetRequest.objects.create(email=email, user=user_obj)
            messages.success(request, "Votre demande a été transmise à l'Administrateur. Il réinitialisera votre mot de passe sous peu.")
            return redirect('login')
        else:
            messages.error(request, "Veuillez saisir une adresse email valide.")

    return render(request, 'authentication/forgot_password.html')


def logout_view(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('login')
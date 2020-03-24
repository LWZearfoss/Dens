from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm

from .forms import RegistrationForm, EmailChangeForm
from .models import DenModel


def logout_view(request):
    logout(request)
    return redirect("/")


def register_view(request):
    if request.method == "POST":
        registration_form_object = RegistrationForm(request.POST)
        if registration_form_object.is_valid():
            registration_form_object.save()
            return redirect("/login/")
    else:
        registration_form_object = RegistrationForm()
    context = {
        "registration_form": registration_form_object,
    }
    return render(request, "registration/register.html", context=context)


@login_required
def index_view(request):
    context = {}
    return render(request, 'dens/index.html', context)


@login_required
def den_view(request, den_slug):
    den_object = get_object_or_404(DenModel, slug=den_slug)
    context = {'den_slug': den_object.slug}
    return render(request, 'dens/den.html', context)


@login_required
def profile_view(request):
    context = {}
    return render(request, 'dens/profile.html', context)


@login_required
def password_view(request):
    if request.method == 'POST':
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(
                request, 'Your password was successfully updated!')
            return redirect('/profile/')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        password_form = PasswordChangeForm(request.user)
    context = {'password_form': password_form}
    return render(request, 'dens/password.html', context)


@login_required
def email_view(request):
    if request.method == 'POST':
        email_form = EmailChangeForm(request.user, request.POST)
        if email_form.is_valid():
            email_form.save()
            return redirect('/profile/')
    else:
        email_form = EmailChangeForm(request.user)
    context = {'email_form': email_form}
    return render(request, 'dens/email.html', context)


@login_required
def delete_view(request):
    request.user.delete()
    return redirect("/")

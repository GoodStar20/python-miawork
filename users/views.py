from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users import forms
from django.contrib.auth.models import User
from .serializers import UserSerializer
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from rest_framework import viewsets

from urllib.parse import urlparse

PASSWORD='password123!'

def AuthView(request, uw):
    #print("REQUEST META")
    #print(request.META)
    # uw: underwriter 3-letter initials
    user = authenticate(username=uw, password=PASSWORD)
    redirect_url_name = 'listview'
    login(request, user)

    if user == None:
        # automatically set redirect to home
        redirect_url_name = 'home'
        messages.error(request, "Could not log you in")
    else:
        messages.success(request, "You were logged in")
    return HttpResponseRedirect(reverse(redirect_url_name))


@login_required
def UserEditView(request):
    if request.method == 'POST':
        form = forms.UserForm(request.POST, instance=request.user or None)
        if form.is_valid():
            form.save()
            messages.success(request, f'Account has been updated')
            return redirect('profile')

    form = forms.UserForm(instance=request.user or None)
    title = "Profile"
    context = {'form': form,  'title': title, 'META_INFO': request.META.get('HTTP_REFERER'), #'root_url': request.get_host()
        }
    return render(request, 'users/profile.html', context)



"""
Django Rest API
"""
class RestView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

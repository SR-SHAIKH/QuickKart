from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import ProfileUpdateForm

# -------------------- Edit Profile View --------------------
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # change to your profile URL name if needed
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'dashboard/edit_profile.html', {'form': form})


# -------------------- Password Change View --------------------
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('password_change_done')  # You can change this to 'profile' if you want

@login_required
def customer_profile_view(request):
    if request.user.role != 'customer':
        return redirect('home')
    return render(request, 'dashboard/customer_profile.html', {'user': request.user})

@login_required
def owner_profile_view(request):
    if request.user.role != 'shop_owner':
        return redirect('home')
    return render(request, 'dashboard/owner_profile.html', {'user': request.user})

@login_required
def customer_edit_profile(request):
    if request.user.role != 'customer':
        return redirect('home')
    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('customer_profile')
    return render(request, 'dashboard/customer_edit_profile.html', {'form': form})


@login_required
def owner_edit_profile(request):
    if request.user.role != 'shop_owner':
        return redirect('home')
    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('owner_profile')
    return render(request, 'dashboard/owner_edit_profile.html', {'form': form})


from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from .forms import ProfileUpdateForm


# -------------------- Profile View --------------------
@login_required
def profile_view(request):
    return render(request, 'dashboard/profile.html')


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

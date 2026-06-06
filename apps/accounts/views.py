
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
import uuid
 
from .models import User, PasswordResetToken
from .forms import (
    LoginForm, RegisterForm, ProfileForm, ChangePasswordForm,
    ForgotPasswordForm, ResetPasswordForm, UserManagementForm
)
from .decorators import admin_required
 
 
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user)
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            messages.success(request, f'Welcome back, {user.name}!')
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)
    return render(request, 'accounts/login.html', {'form': form})
 
 
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')
 
 
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('accounts:login')
    return render(request, 'accounts/register.html', {'form': form})
 
 
def forgot_password_view(request):
    form = ForgotPasswordForm()
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = str(uuid.uuid4())
                PasswordResetToken.objects.create(user=user, token=token)
                reset_url = request.build_absolute_uri(f'/accounts/reset-password/{token}/')
                print(f"[PASSWORD RESET] URL: {reset_url}")
                messages.success(request, 'Password reset link sent to your email.')
            except User.DoesNotExist:
                messages.success(request, 'If that email exists, a reset link was sent.')
            return redirect('accounts:login')
    return render(request, 'accounts/forgot_password.html', {'form': form})
 
 
def reset_password_view(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if not reset_token.is_valid():
            messages.error(request, 'This reset link has expired or already been used.')
            return redirect('accounts:login')
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid reset link.')
        return redirect('accounts:login')
 
    form = ResetPasswordForm()
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            reset_token.user.set_password(form.cleaned_data['password'])
            reset_token.user.save()
            reset_token.is_used = True
            reset_token.save()
            messages.success(request, 'Password reset successful. Please log in.')
            return redirect('accounts:login')
    return render(request, 'accounts/reset_password.html', {'form': form, 'token': token})
 
 
@login_required
def profile_view(request):
    form = ProfileForm(instance=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'form': form})
 
 
@login_required
def change_password_view(request):
    form = ChangePasswordForm()
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            user = request.user
            if not user.check_password(form.cleaned_data['current_password']):
                messages.error(request, 'Current password is incorrect.')
            else:
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully.')
                return redirect('accounts:profile')
    return render(request, 'accounts/change_password.html', {'form': form})
 
 
@login_required
@admin_required
def user_list_view(request):
    query = request.GET.get('q', '')
    role = request.GET.get('role', '')
    status = request.GET.get('status', '')
 
    users = User.objects.all()
    if query:
        users = users.filter(Q(name__icontains=query) | Q(email__icontains=query) | Q(company__icontains=query))
    if role:
        users = users.filter(role=role)
    if status:
        users = users.filter(is_active=(status == 'active'))
 
    paginator = Paginator(users, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
 
    context = {
        'page_obj': page_obj,
        'query': query,
        'role': role,
        'status': status,
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'inactive_users': User.objects.filter(is_active=False).count(),
    }
    return render(request, 'accounts/user_list.html', context)
 
 
@login_required
@admin_required
def user_create_view(request):
    form = UserManagementForm()
    if request.method == 'POST':
        form = UserManagementForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password('VendorBridge@123')
            user.save()
            messages.success(request, f'User {user.name} created. Default password: VendorBridge@123')
            return redirect('accounts:user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Create User'})
 
 
@login_required
@admin_required
def user_edit_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserManagementForm(instance=user)
    if request.method == 'POST':
        form = UserManagementForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('accounts:user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Edit User', 'edit_user': user})
 
 
@login_required
@admin_required
def user_toggle_status_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'You cannot deactivate your own account.')
    else:
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.name} has been {status}.')
    return redirect('accounts:user_list')
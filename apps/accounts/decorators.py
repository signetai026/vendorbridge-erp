
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
 
 
def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.role != 'admin' and not request.user.is_superuser:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return wrapper
 
 
def manager_or_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.role not in ['admin', 'manager'] and not request.user.is_superuser:
            messages.error(request, 'Access denied.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return wrapper
 
 
def procurement_access_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        allowed_roles = ['admin', 'manager', 'procurement_officer']
        if request.user.role not in allowed_roles and not request.user.is_superuser:
            messages.error(request, 'Access denied.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return wrapper
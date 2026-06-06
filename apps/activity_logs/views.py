from django.shortcuts import render

def activity_log_list(request):
    return render(request, 'activity_logs/activity_log_list.html')
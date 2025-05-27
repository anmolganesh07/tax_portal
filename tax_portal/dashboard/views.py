from django.shortcuts import render

# Create your views here.
def home_view(request):
    return render(request, 'landing.html')

def itr_home_view(request):
    return render(request, 'dashboard/itr_home.html')

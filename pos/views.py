from django.shortcuts import render

def pos_home(request):
    return render(request, 'pos/pos_home.html')
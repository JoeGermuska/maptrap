# Create your views here.
from django.shortcuts import render
def index(request):
    return render(request, 'index.html',{})
    
def generate_workbook(request):
    """Given some input, return an Excel spreadsheet"""
    pass
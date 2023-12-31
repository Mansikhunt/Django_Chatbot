from django.shortcuts import render, redirect
from django.http import JsonResponse
import google.generativeai as genai

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat

from django.utils import timezone

GOOGLE_API_KEY = 'YOUR_API_KEY'
genai.configure(api_key=GOOGLE_API_KEY)

def generate(message):
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(
             message,
             generation_config={
                  "max_output_tokens": 2048,
                  "temperature": 0.9,
                  "top_p": 1
             },
             stream=False,
        )
        output = response.candidates[0].content.parts[0].text
        return output

    
# Create your views here.
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)
    if request.method == 'POST':
        message = request.POST.get('message') 
        response = generate(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats})

def login(request):
     if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
     else:
        return render(request, 'login.html')

def register(request):
     if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1==password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
            return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = "Password don't match" 
            return render(request, 'register.html', {'error_message': error_message})
     return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login')
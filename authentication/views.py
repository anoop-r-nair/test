from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
import firebase_admin
from firebase_admin import auth, credentials, firestore
import os

# Initialize Firebase Admin SDK
cred_path = os.path.join(os.path.dirname(__file__), 'C:/Users/Anoop/sports_team_management/sports_team_management/athletarena-firebase-adminsdk-q957f-b59ba119bd.json')
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
db = firestore.client()

def home(request):
    return render(request, 'accounts/home.html')

def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = auth.create_user(email=email, password=password)
            # Save user details to Firestore
            user_ref = db.collection('users').document(user.uid)
            user_ref.set({
                'email': email,
                'uid': user.uid,
            })
            messages.success(request, 'User created successfully')
            return redirect('login')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'accounts/signup.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            # Firebase does not provide direct password authentication using Admin SDK
            # Use Firebase Authentication client SDK in the frontend for password verification
            user = auth.get_user_by_email(email)
            # Validate the password on the frontend
            messages.success(request, 'Login successful')
            return redirect('home')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'accounts/login.html')

def admin_login(request):
    return render(request, 'accounts/admin_login.html')

@staff_member_required
def admin_dashboard(request):
    users_ref = db.collection('users')
    users = [doc.to_dict() for doc in users_ref.stream()]
    return render(request, 'accounts/admin_dashboard.html', {'users': users})

@staff_member_required
def delete_user(request, user_id):
    try:
        auth.delete_user(user_id)
        db.collection('users').document(user_id).delete()
        messages.success(request, 'User deleted successfully')
    except Exception as e:
        messages.error(request, str(e))
    return redirect('admin_dashboard')

def coach_dashboard(request):
    return render(request, 'accounts/coach_dashboard.html')

def player_dashboard(request):
    return render(request, 'accounts/player_dashboard.html')

def parent_dashboard(request):
    return render(request, 'accounts/parent_dashboard.html')

def medical_staff_dashboard(request):
    return render(request, 'accounts/medical_staff_dashboard.html')

def sports_psychologist_dashboard(request):
    return render(request, 'accounts/sports_psychologist_dashboard.html')

def analytics_expert_dashboard(request):
    return render(request, 'accounts/analytics_expert_dashboard.html')

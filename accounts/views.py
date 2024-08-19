from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
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

# Home view
def home(request):
    return render(request, 'accounts/home.html')

# Signup view
def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        name = request.POST.get('name')
         # The user's role
        try:
            # Create a new user in Firebase Authentication
            user = auth.create_user(email=email, password=password)
            
            # Save the user's details in Firestore
            user_ref = db.collection('users').document(user.uid)
            user_ref.set({
                'email': email,
                'uid': user.uid,
                'address': address,
                'phone': phone,
                'name': name,
            })
            messages.success(request, 'User created successfully')
            return redirect('login')
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'accounts/signup.html')

def signupcoach(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        name = request.POST.get('name')
        
        try:
            # Create a new user in Firebase Authentication
            user = auth.create_user(email=email, password=password)
            
            # Save the user's details in Firestore with 'uid' as document ID
            user_ref = db.collection('coaches').document(user.uid)
            user_ref.set({
                'email': email,
                'uid': user.uid,  # Store uid
                'address': address,
                'phone': phone,
                'name': name,
            })
            messages.success(request, 'Coach created successfully')
            return redirect('login')  # Ensure 'login' is a valid URL name
        except Exception as e:
            # Log the exception (optional)
            print(f"Error creating coach: {e}")
            messages.error(request, f"Error: {str(e)}")
            return redirect('signupcoach')  # Redirect back to signup on error
    else:
        return render(request, 'accounts/signupcoach.html')
    
def signupparent(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        name = request.POST.get('name')
        
        try:
            # Create a new user in Firebase Authentication
            user = auth.create_user(email=email, password=password)
            
            # Save the user's details in Firestore with 'uid' as document ID
            user_ref = db.collection('parents').document(user.uid)
            user_ref.set({
                'email': email,
                'uid': user.uid,  # Store uid
                'address': address,
                'phone': phone,
                'name': name,
            })
            messages.success(request, 'Coach created successfully')
            return redirect('login')  # Ensure 'login' is a valid URL name
        except Exception as e:
            # Log the exception (optional)
            print(f"Error creating coach: {e}")
            messages.error(request, f"Error: {str(e)}")
            return redirect('signupparent')  # Redirect back to signup on error
    else:
        return render(request, 'accounts/signupparent.html')    

# Login view

def coach_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = auth.get_user_by_email(email)
            coach_ref = db.collection('coaches').document(user.uid)
            coach_doc = coach_ref.get()
            
            if coach_doc.exists:
                # Coach exists, proceed to login
                # Your logic to render dashboard or homepage for coach
                return render(request, 'accounts/manage_team.html', {'coach': coach_doc.to_dict()})
            else:
                return JsonResponse({'error': 'You are not registered as a coach.'})
        
        except Exception as e:
            return JsonResponse({'error': str(e)})
    
    return render(request, 'login.html')

# Admin login view (optional, depending on how you handle admin login)
def admin_login(request):
    return render(request, 'accounts/admin_login.html')

# Admin dashboard view
@staff_member_required
def admin_dashboard(request):
    users_ref = db.collection('users')
    users = [doc.to_dict() for doc in users_ref.stream()]
    return render(request, 'accounts/admin_dashboard.html', {'users': users})

def create(request):
    if request.method == 'POST':
        coachname = request.POST.get('coachname')
        players = request.POST.get('players').split(',')  # Split player names into a list
        teamname = request.POST.get('teamname')

        try:
            # Save the team details in Firestore
            team_ref = db.collection('teams').document()
            team_ref.set({
                'coachname': coachname,
                'players': players,
                'teamname': teamname,
            })
            messages.success(request, 'Team created successfully')
            return redirect('manage_teams')  # Replace with the actual URL name for managing teams
        except Exception as e:
            messages.error(request, f"Error creating team: {str(e)}")

    return render(request, 'accounts/manage_team.html')



# Delete user view (only for admin)
@staff_member_required
def delete_user(request, email):
    try:
        # Fetch the user by email
        user = auth.get_user_by_email(email)
        # Delete the user from Firebase Authentication
        auth.delete_user(user.uid)
        # Delete the user document from Firestore
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).stream()
        for doc in query:
            doc.reference.delete()
        messages.success(request, 'User deleted successfully')
    except Exception as e:
        messages.error(request, str(e))
    return redirect('admin_dashboard')

# Update user view (only for admin)
@staff_member_required
def update_user(request, email):
    try:
        # Fetch user details from Firestore
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).stream()
        user_doc = None
        doc_reference = None
        for doc in query:
            user_doc = doc.to_dict()
            doc_reference = doc.reference
            break
        
        if request.method == 'POST':
            name = request.POST.get('name')
            address = request.POST.get('address')
            phone = request.POST.get('phone')
            users = request.POST.get('users')
            
            # Update user details in Firestore
            if user_doc:
                doc_reference.update({
                    'name': name,
                    'address': address,
                    'phone': phone,
                    'users': users,
                })
                messages.success(request, 'User updated successfully')
                return redirect('admin_dashboard')
        
        return render(request, 'accounts/update_user.html', {'user': user_doc})

    except Exception as e:
        messages.error(request, str(e))
        return redirect('admin_dashboard')
    
# def coaches_view(request):
#     try:
#         coaches_ref = db.collection('coaches')
#         docs = coaches_ref.stream()

#         coaches_list = []
#         for doc in docs:
#             coach_data = doc.to_dict()
#             print(coach_data)  # This will print the coach data in the console
#             coaches_list.append(coach_data)

#         return render(request, 'accounts/coaches.html', {'coaches': coaches_list})

#     except Exception as e:
#         print("Error:", str(e))
#         return render(request, 'accounts/coaches.html', {'error': str(e), 'coaches': []})


def update_coach_by_email(request, email):
    coaches_ref = db.collection('coaches')
    query = coaches_ref.where('email', '==', email).limit(1).get()

    if not query:
        return render(request, 'accounts/error.html', {'message': 'Coach not found'})

    coach_ref = query[0].reference  # Get the document reference

    if request.method == 'POST':
        # Get data from the form
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        # Update the Firestore document
        coach_ref.update({
            'name': name,
            'address': address,
            'phone': phone,
        })
        return redirect('coaches')  # Redirect back to the coaches list

    # For GET request, display the current coach data
    coach = coach_ref.get().to_dict()
    return render(request, 'accounts/update_coach.html', {'coach': coach})

def delete_coach_by_email(request, email):
    coaches_ref = db.collection('coaches')
    query = coaches_ref.where('email', '==', email).limit(1).get()

    if not query:
        return render(request, 'accounts/error.html', {'message': 'Coach not found'})

    coach_ref = query[0].reference  # Get the document reference
    coach_ref.delete()
    return redirect('coaches')  # Redirect back to the coaches list

def update_parent_by_email(request, email):
    parents_ref = db.collection('parents')
    query = parents_ref.where('email', '==', email).limit(1).get()

    if not query:
        return render(request, 'accounts/error.html', {'message': 'Parent not found'})

    parent_ref = query[0].reference  # Get the document reference

    if request.method == 'POST':
        # Get data from the form
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        # Update the Firestore document
        parent_ref.update({
            'name': name,
            'address': address,
            'phone': phone,
        })
        return redirect('parents')  # Redirect back to the parents list

    # For GET request, display the current parent data
    parent = parent_ref.get().to_dict()
    return render(request, 'accounts/update_parent.html', {'parent': parent})

def delete_parent_by_email(request, email):
    parents_ref = db.collection('parents')
    query = parents_ref.where('email', '==', email).limit(1).get()

    if not query:
        return render(request, 'accounts/error.html', {'message': 'Parent not found'})

    parent_ref = query[0].reference  # Get the document reference
    parent_ref.delete()
    return redirect('parents')  # Redirect back to the parents list



@staff_member_required
# def manage_teams(request):
#     try:
#         # Retrieve all coaches
#         coaches_ref = db.collection('coaches')
#         coaches_docs = coaches_ref.stream()
#         coaches = [{'email': doc.id, **doc.to_dict()} for doc in coaches_docs]

#         # Retrieve all players
#         players_ref = db.collection('users').where('role', '==', 'player')
#         players_docs = players_ref.stream()
#         players = [{'email': doc.id, **doc.to_dict()} for doc in players_docs]

#         # Retrieve all teams
#         teams_ref = db.collection('teams')
#         teams_docs = teams_ref.stream()
#         teams = [{'id': doc.id, **doc.to_dict()} for doc in teams_docs]

#         return render(request, 'manage_team.html', {
#             'coaches': coaches,
#             'players': players,
#             'teams': teams,
#         })
#     except Exception as e:
#         messages.error(request, f'Error retrieving data: {e}')
#         return redirect('manage_team')

@staff_member_required
def edit_team_by_email(request, coach_email):
    teams_ref = db.collection('teams')
    team_query = teams_ref.where('coach_email', '==', coach_email).stream()
    team_doc = next(team_query, None)

    if not team_doc:
        messages.error(request, 'Team not found')
        return redirect('manage_teams')

    team = team_doc.to_dict()

    users_ref = db.collection('users')
    users = [doc.to_dict() for doc in users_ref.stream()]
    coaches = [user for user in users if user.get('role') == 'coach']
    players = [user for user in users if user.get('role') == 'player']

    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        new_coach_email = request.POST.get('coach_email')
        player_emails = request.POST.getlist('player_emails')

        team_doc.reference.update({
            'team_name': team_name,
            'coach_email': new_coach_email,
            'players': player_emails,
        })

        messages.success(request, 'Team updated successfully')
        return redirect('manage_teams')

    return render(request, 'accounts/edit_team.html', {
        'team': team,
        'coaches': coaches,
        'players': players,
    })


@staff_member_required
def delete_team_by_email(request, coach_email):
    try:
        # Find the team document where the coach_email matches
        teams_ref = db.collection('teams')
        team_query = teams_ref.where('coach_email', '==', coach_email).stream()
        team_doc = next(team_query, None)

        if not team_doc:
            messages.error(request, 'Team not found')
            return redirect('manage_teams')

        # Delete the team document
        team_doc.reference.delete()
        messages.success(request, 'Team deleted successfully')
    except Exception as e:
        messages.error(request, str(e))

    return redirect('manage_teams')


# Role-specific dashboard views
def coach_dashboard(request):
    return render(request, 'accounts/coach_dashboard.html')

def player_dashboard(request):
    return render(request, 'accounts/player_dashboard.html')

def medical_staff_dashboard(request):
    return render(request, 'accounts/medical_staff_dashboard.html')

def sports_psychologist_dashboard(request):
    return render(request, 'accounts/sports_psychologist_dashboard.html')

def analytics_expert_dashboard(request):
    return render(request, 'accounts/analytics_expert_dashboard.html')

# Additional views for the app's features
def modules(request):
    return render(request, 'accounts/modules.html')

def schedules(request):
    return render(request, 'accounts/schedules.html')

def teams(request):
    return render(request, 'accounts/teams.html')

def players(request):
    return render(request, 'accounts/players.html')

def parents(request):
    parents_ref = db.collection('parents')
    parents_docs = parents_ref.stream()

    # Collecting parent data into a list
    parents = []
    for doc in parents_docs:
        parent = doc.to_dict()
        parents.append(parent)

    return render(request, 'accounts/parents.html', {'parents': parents})

def manage_team(request):
    # Your logic here
    return render(request, 'accounts/manage_team.html') 

def login(request):
    return render(request, 'accounts/login.html')

def coaches(request):
    try:
        # Fetch all coaches from Firestore
        coaches_ref = db.collection('coaches')
        coaches = [doc.to_dict() for doc in coaches_ref.stream()]
        print(coaches)  # For debugging: Print the coaches data
        return render(request, 'accounts/coaches.html', {'coaches': coaches})
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return render(request, 'accounts/coaches.html', {'coaches': []})




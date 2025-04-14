from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login 
from django.http import HttpResponse
from .models import UserProfile,Project,Department,DepartmentHead,Task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth import logout
from django.db.models import Q
from django.http import JsonResponse


def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        role = request.POST.get('role')
        code = request.POST.get('code')
        phone = request.POST.get('phone')
        file_upload = request.FILES.get('file_upload')

        # Determine the correct department field based on the role
        department_name = None
        if role == 'department_head':
            department_name = request.POST.get('department_head_department')
        elif role == 'supervisor':
            department_name = request.POST.get('supervisor_department')
        elif role == 'technician':
            department_name = request.POST.get('technician_department')

        # Basic validation
        if not all([first_name, last_name, username, password, confirm_password, phone]):
            return HttpResponse("All fields are required.", status=400)

        if password != confirm_password:
            return HttpResponse("Passwords do not match.", status=400)

        # Create user
        user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email)

        # Handle department assignment
        department = None
        if department_name:
            department, created = Department.objects.get_or_create(name=department_name)

        # Create user profile
        UserProfile.objects.create(
            user=user,
            role=role,
            department=department,  # Store the correct department
            code=code,
            phone=phone,
            file_upload=file_upload
        )

        # Create DepartmentHead instance if the role is 'department_head'
        if role == 'department_head' and department:
            # Check if a DepartmentHead already exists for this department
            department_head, created = DepartmentHead.objects.get_or_create(
                user=user,
                defaults={'department': department}
            )
            if not created:
                # If a DepartmentHead already exists for this department, update it
                department_head.user = user
                department_head.save()

        # Log the user in
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)

        # Send welcome email
        subject = 'Welcome to Infralink!'
        html_message = render_to_string('registrationmail.html', {'user': user, 'current_year': timezone.now().year})
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        email = EmailMultiAlternatives(subject, plain_message, from_email, recipient_list)
        email.attach_alternative(html_message, "text/html")
        email.send()

        return redirect('login')  # Redirect to a success page or another view

    return render(request, 'registration.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user is not None:
            # Log the user in
            login(request, user)

            # Get the associated profile for the authenticated user
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                profile = None

            # Redirect based on the user's role
            if profile:
                if profile.role == 'project_head':
                    return redirect('dashboard_projecthead')
                elif profile.role == 'department_head':
                    return redirect('departmentdashboard')
                # Add more role-based redirections as needed
            else:
                # If no profile, redirect to a default page or handle accordingly
                return redirect('home')  # Or some default page
        else:
            # If authentication fails, redirect to login
            return redirect('login')

    # Render login page if the request method is GET
    return render(request, 'login.html')

def home_view(request):
    return render(request,'home.html')
from django.db.models import Sum

def index_projecthead(request):
    user = request.user
    item = UserProfile.objects.get(user=user)
    item1 = Project.objects.filter(project_head_id=item.id)

    # Calculate total budget
    total_budget = Project.objects.filter(project_head_id=item.id).aggregate(Sum('budget'))['budget__sum'] or 0

    # Count total number of projects
    total_projects = Project.objects.filter(project_head_id=item.id).count()

    # Count projects by status
    ongoing_projects = Project.objects.filter(status="ongoing",project_head_id=item.id).count()
    completed_projects = Project.objects.filter(status="completed",project_head_id=item.id).count()
    pending_projects = Project.objects.filter(status="pending",project_head_id=item.id).count()
    projects = Project.objects.all()

    # Dictionary to store collision details
    projects = Project.objects.all()

    # Dictionary to store collision details
    collision_details = []

    for project in projects:
        # Check for location collisions
        location_collisions = Project.objects.filter(location=project.location).exclude(id=project.id)
        
        # Check for date collisions where projects overlap in any manner
        date_collisions = Project.objects.filter(
            Q(start_date__lt=project.end_date) & Q(end_date__gt=project.start_date)
        ).exclude(id=project.id)
        
        # Combine collisions
        all_collisions = location_collisions | date_collisions

        if all_collisions.exists():
            collision_details.append({
                'project': project,
                'collisions': all_collisions
            })

    return render(request, 'index-projecthead.html', {
        'user': user,
        'item': item,
        'item1': item1,
        'total_budget': total_budget,
        'total_projects': total_projects,
        'ongoing_projects': ongoing_projects,
        'completed_projects': completed_projects,
        'pending_projects': pending_projects,
        'collision_details': collision_details,
    })
def projecthead_profile_view(request):
    user = request.user
    item = UserProfile.objects.get(user=user)
    return render(request,'users-profile.html',{'user':user,'item':item})
def createproject_view(request):
    if request.method == 'POST':
        project_name = request.POST.get('projectName')
        description = request.POST.get('description')
        project_head_name = request.POST.get('projectHead')
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        location = request.POST.get('location')
        status = request.POST.get('status')
        budget = request.POST.get('budget')
        department_names = request.POST.get('departments').split(',')
        p1=request.POST.get('p1')
        p2=request.POST.get('p2')
        p3=request.POST.get('p3')
        project_head = User.objects.get(username=project_head_name)
        project = Project(
            project_name=project_name,
            description=description,
            project_head=project_head,
            start_date=start_date,
            end_date=end_date,
            location=location,
            status=status,
            budget=budget,
            p1=p1,
            p2=p2,
            p3=p3,
        )
        project.save()
        departments = Department.objects.filter(name__in=department_names)
        project.departments.set(departments)
        project.save()
        return redirect('dashboard_projecthead')

    return render(request,'createproject.html')

def sign_out_projecthead(request):
    logout(request)
    return redirect('home')

from django.shortcuts import render, get_object_or_404, redirect


def deleteproject_view(request, project_id):
    # Fetch the project, or return a 404 if it does not exist
    project = get_object_or_404(Project, id=project_id)
    
    # Delete the project
    project.delete()
    print("problem")
    
    # Redirect to the dashboard or another page
    return redirect('dashboard_projecthead')
def departmenthead_view(request):
    user = request.user
    
    # Debugging: Print user details
    print(f"User: {user.username}")
    
    # Get the user's department head profile
    try:
        department_head = DepartmentHead.objects.get(user=user)
        department = department_head.department
        print(f"Department: {department.name}")  # Print department name for debugging
    except DepartmentHead.DoesNotExist:
        department = None
        print("No DepartmentHead profile found.")

    # If the user is a department head, fetch the projects related to their department
    if department:
        projects = Project.objects.filter(departments=department)
        
        # Debugging: Print number of projects and their details
        print(f"Projects Count: {projects.count()}")
        for project in projects:
            print(f"Project: {project.project_name}, Budget: {project.budget}")

        # Calculate total budget and total number of projects
        total_budget = projects.aggregate(total=Sum('budget'))['total'] if projects else 0
        total_projects = projects.count()
    else:
        projects = None
        total_budget = 0
        total_projects = 0
    ongoing_projects = Project.objects.filter(status="ongoing",departments=department).count()
    completed_projects = Project.objects.filter(status="completed",departments=department).count()
    pending_projects = Project.objects.filter(status="pending",departments=department).count()

    return render(request, 'departmentdashboard.html', {
        'user': user,
        'projects': projects,
        'department': department,
        'total_budget': total_budget,
        'total_projects': total_projects,
        'ongoing_projects': ongoing_projects,
        'completed_projects': completed_projects,
        'pending_projects': pending_projects,
    })

def department_profile_view(request):
    user = request.user
    item = UserProfile.objects.get(user=user)
    return render(request,'departmentprofile.html',{'user':user,'item':item})
def search_view(request):
    return render(request, 'search.html')
# views.py

from geopy.distance import geodesic
from django.shortcuts import render
import requests

def fetch_coordinates(location):
    """Fetch latitude and longitude using OpenCage API."""
    api_key = '9673710c9e99483ca40dd0cecce442a2'  # Replace with your API key
    opencage_url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={api_key}"
    response = requests.get(opencage_url)
    if response.status_code == 200:
        location_data = response.json()
        if location_data['results']:
            lat = location_data['results'][0]['geometry']['lat']
            lon = location_data['results'][0]['geometry']['lng']
            return float(lat), float(lon)
    return None, None

def shop_search(request):
    if request.method == 'POST':
        place = request.POST.get('place')
        max_distance_km = request.POST.get('max_distance')
        user_lat, user_lon = fetch_coordinates(place)  # Get user input location's coordinates

        if not user_lat or not user_lon:
            return render(request, 'shops.html', {'shops': [], 'place': place, 'error': 'Location not found'})

        try:
            max_distance_km = float(max_distance_km)  # Convert to float
        except ValueError:
            max_distance_km = 10  # Default if invalid input

        projects = Project.objects.all()
        shops = []

        for project in projects:
            shop_lat, shop_lon = fetch_coordinates(project.location)
            if shop_lat and shop_lon:
                distance = geodesic((user_lat, user_lon), (shop_lat, shop_lon)).kilometers
                if distance <= max_distance_km:
                    shops.append({
                        'lat': shop_lat,
                        'lon': shop_lon,
                        'name': project.project_name,
                        'location': project.location,
                        'distance': round(distance, 2)
                    })

        # Pass the user location and shop data to the template
        return render(request, 'shops.html', {
            'shops': shops,
            'place': place,
            'user_lat': user_lat,
            'user_lon': user_lon,
            'max_distance': max_distance_km
        })

    return render(request, 'search.html')
from .models import Post, Replie


def forum(request):
    project_id = request.GET.get('project_id')
    print(project_id)
    if request.method == "POST":
        project_id = request.GET.get('project_id')
        print("in post:",project_id)
        user = request.user
        content = request.POST.get('content', '')
        if project_id is not None:
            post = Post(user1=user, post_content=content, project_id1=project_id)
            print(post)
            post.save()
            alert = True
        else:
            alert = False  # or handle this case differently
            print("Error: project_id is None")
            
        return render(request, "forum.html", {'alert': alert,'project_id':project_id})
    
    posts = Post.objects.filter(project_id1=project_id).order_by('-timestamp')
    return render(request, "forum.html", {'posts': posts,'project_id':project_id})


def discussion(request):
    post_id1=request.GET.get('post_id')
    print(post_id1)
    post = Post.objects.get(id=post_id1)
    replies = Replie.objects.filter(post_id=post_id1)
    if request.method=="POST":
        user = request.user
        desc = request.POST.get('desc','')
        post_id =request.POST.get('post_id','')
        reply = Replie(user = user, reply_content = desc, post=post)
        reply.save()
        alert = True
        return render(request, "discussion.html", {'alert':alert,'post_id':post_id})
    return render(request, "discussion.html", {'post':post, 'replies':replies})


def task_management_view(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        # Adding a new task via AJAX
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        due_date = request.POST.get('due_date')

        # Create and save a new task
        task = Task.objects.create(
            project=project,
            description=description,
            priority=priority,
            due_date=due_date
        )

        # Return the task as JSON to update the task list dynamically
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'description': task.description,
                'priority': task.priority,
                'due_date': task.due_date.strftime('%Y-%m-%d'),
                'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })

    # Fetch all tasks related to the project, ordered by priority
    tasks = project.tasks.all().order_by('priority')

    return render(request, 'task.html', {
        'project': project,
        'tasks': tasks
    })
from django.shortcuts import render

def serve_pchart(request):
    return render(request, 'pchart.html')



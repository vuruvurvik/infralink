"""infralink URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from infra.views import (
    register,
    login_view,
    home_view,
    index_projecthead,
    projecthead_profile_view,
    createproject_view,
    sign_out_projecthead,
    deleteproject_view,
    departmenthead_view,
    department_profile_view,
    search_view,
    shop_search,
    forum,
    discussion,
    task_management_view,
    serve_pchart,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',login_view,name='login'),
    path('registration/',register,name='register'),
    path('',home_view,name="home"),
    path('projecthead_dashboard/',index_projecthead,name='dashboard_projecthead'),
    path('projecthead_profile/',projecthead_profile_view,name="projecthead_profile"),
    path('createproject/',createproject_view,name="createproject"),
    path('logout/',sign_out_projecthead,name="logout_projecthead"),
    path('delete/<int:project_id>/', deleteproject_view, name='delete_project'),
    path('departmentdashboard/',departmenthead_view,name='departmentdashboard'),
    path('departmentprofile',department_profile_view,name='departmentprofile'),
    path('search/',search_view, name='search_view'),
    path('shops/',shop_search,name='shop_search'),
    path("forum/",forum, name="Forum"),
    path("discussion/",discussion, name="Discussions"),
    path('tasks/<int:project_id>/', task_management_view, name='task_management'),
    path('pchart/',serve_pchart, name='serve_pchart'),
]
    
from django.conf.urls.static import static
from django.conf import  settings    
urlpatterns  += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

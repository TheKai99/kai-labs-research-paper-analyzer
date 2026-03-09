"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from app import views

urlpatterns = [
    # For admin portal
    path("admin/", admin.site.urls),

    #for user Registration
    path("register/", views.register_view, name="register"),

    # For login when user already exist
    path("login/", views.login_view, name="login"),

    # Logout page
    path("logout/", views.logout_view, name="logout"),


    # Home section index.html
    path("", views.upload_pdf, name="upload"),

    # For user history uploads
    path("history/",views.history_view,name="history"),
    path("paper/<int:paper_id>/", views.paper_detail, name="paper_detail"),#for specific paper details
    

    # For comparision b/w two papers
    path("compare-pdf/", views.compare_pdfs, name="compare_pdfs"),


    # For paper search section
    path("search-papers/", views.paper_search, name="paper_search"),
]
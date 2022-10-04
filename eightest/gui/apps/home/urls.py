from . import views
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('', views.home, name="home")
]
urlpatterns += staticfiles_urlpatterns()

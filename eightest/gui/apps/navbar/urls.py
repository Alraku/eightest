from django.urls import path
from . import views as navbar_views
from ..home import views as home_views


urlpatterns = [
    path("function", navbar_views.function, name="function"),
    path("", home_views.home, name="home"),
    path("chris", navbar_views.chris, name="chris"),
    path('get_response', navbar_views.answer_me, name='get_response')
]

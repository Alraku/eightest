from . import views
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('history', views.HistoryView.as_view(), name="history")
]
urlpatterns += staticfiles_urlpatterns()
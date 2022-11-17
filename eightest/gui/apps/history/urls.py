from . import views
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('history', views.HistoryView.as_view(), name="history"),
    path('get_response_hist', views.HistoryView.answer_me_hist, name="get_response_hist")
]
urlpatterns += staticfiles_urlpatterns()
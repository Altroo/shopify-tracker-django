from django.urls import path
from .views import BlankView

app_name = 'shops'

urlpatterns = [
    # GET :
    path('', BlankView.as_view()),
]

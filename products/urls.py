from django.urls import path
from .views import BlankView

app_name = 'products'

urlpatterns = [
    # GET :
    path('', BlankView.as_view()),
]

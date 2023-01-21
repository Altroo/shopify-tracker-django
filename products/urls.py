from django.urls import path
from .views import ProductsView

app_name = 'products'

urlpatterns = [
    # GET :
    path('', ProductsView.as_view()),
]

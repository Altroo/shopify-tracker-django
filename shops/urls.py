from django.urls import path
from .views import ShopView, ConfigsView

app_name = 'shops'

urlpatterns = [
    # GET :
    path('', ShopView.as_view()),
    path('configs/', ConfigsView.as_view()),
]

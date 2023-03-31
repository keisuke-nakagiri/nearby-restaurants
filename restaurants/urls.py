from django.urls import path
from . import views

app_name = 'restaurants'
urlpatterns = [
    path('', views.RestaurantsSearchView.as_view(), name='search'),
    path('result/', views.RestaurantsResultView.as_view(), name='result'),
    path('detail/<str:pk>/', views.RestaurantsDetailView.as_view(), name='detail'),
]
from django.urls import path
from . import views

app_name = 'restaurants'
urlpatterns = [
    path('', views.RestaurantsSearchView.as_view(), name='search'),
    path('results/', views.RestaurantsResultsView.as_view(), name='results'),
    path('detail/<str:pk>/', views.RestaurantsDetailView.as_view(), name='detail'),
]
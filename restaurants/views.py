import requests

from django.shortcuts import render
from django.views.generic import TemplateView

from config.settings import HOTPEPPER_API_KEY


class RestaurantsSearchView(TemplateView):
    template_name = 'restaurants_search.html'
    
    
class RestaurantsResultsView(TemplateView):
    template_name = 'restaurants_results.html'

    def post(self, request):
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        range = request.POST.get('range')

        url = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
        params = {
            'key': HOTPEPPER_API_KEY,
            'lat': latitude,
            'lng': longitude,
            'range': range,
            'format': 'json',
        }

        response = requests.get(url, params)
        restaurants = response.json()['results']['shop']
        context = {'restaurants': restaurants}
        return self.render_to_response(context)


class RestaurantsDetailView(TemplateView):
    template_name = 'restaurants_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        id = self.kwargs.get('pk')
        url = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
        params = {
            'key': HOTPEPPER_API_KEY,
            'id': id,
            'format': 'json',
        }
        response = requests.get(url, params)
        restaurant = response.json()['results']['shop'][0]
        context["restaurant"] = restaurant
        return context

import requests

from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from config.settings import HOTPEPPER_API_KEY


class RestaurantsSearchView(TemplateView):
    template_name = 'restaurants_search.html'
    
    
class RestaurantsResultsView(TemplateView):
    template_name = 'restaurants_results.html'

    def get_restaurants_pages(self, restaurants, page=None):
        paginator = Paginator(restaurants, 20)
        try:
            pages = paginator.page(page)
        except PageNotAnInteger:
            pages = paginator.page(1)
        except EmptyPage:
            pages = paginator.page(1)

        return pages

    def post(self, request):
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        search_range = request.POST.get('search_range')
        genre = request.POST.get('genre')

        url = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
        params = {
            'key': HOTPEPPER_API_KEY,
            'lat': latitude,
            'lng': longitude,
            'range': search_range,
            'genre': genre,
            'start': 1,
            'count': 100,
            'format': 'json',
        }

        response = requests.get(url, params)
        data = response.json()
        restaurants = data['results']['shop']
        total_hit_count = data['results']['results_available']

        for i in range(1, total_hit_count // 100 + 1):
            params['start'] = i * 100 + 1
            response = requests.get(url, params)
            restaurants += response.json()['results']['shop']
        
        request.session['restaurants'] = restaurants

        pages = self.get_restaurants_pages(restaurants=restaurants, page=None)
        context = {'restaurants': pages}
        return self.render_to_response(context)
    
    def get(self, request):
        restaurants = request.session.get('restaurants')
        page = request.GET.get('page')
        pages = self.get_restaurants_pages(restaurants=restaurants, page=page)
        context = {'restaurants': pages}
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
        data = response.json()
        restaurant = data['results']['shop'][0]
        context["restaurant"] = restaurant
        return context

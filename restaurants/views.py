import requests

from django.shortcuts import render
from django.views.generic import TemplateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from config.settings import HOTPEPPER_API_KEY


class RestaurantsSearchView(TemplateView):
    template_name = 'restaurants_search.html'
    
    
class RestaurantsResultsView(TemplateView):
    template_name = 'restaurants_results.html'

    SEARCH_RANGE_DICT = {
        '1': '300m',
        '2': '500m',
        '3': '1km',
        '4': '2km',
        '5': '3km',
    }

    SEARCH_BUDGET_DICT = {
        '': '',
        'B009': '〜500円',
        'B010': '501〜1000円',
        'B011': '1001〜1500円',
        'B001': '1501〜2000円',
        'B002': '2001〜3000円',
        'B003': '3001〜4000円',
        'B008': '4001〜5000円',
        'B004': '5001〜7000円',
        'B005': '7001〜10000円',
        'B006': '10001〜15000円',
        'B012': '15001〜20000円',
        'B013': '20001〜30000円',
        'B014': '30001円〜',
    }

    def get_restaurants_pages(self, restaurants, page=None):
        paginator = Paginator(restaurants, 20)
        try:
            pages = paginator.page(page)
        except PageNotAnInteger:
            pages = paginator.page(1)
        except EmptyPage:
            pages = paginator.page(1)

        return pages
    
    def get_genre_name(self, genre_id):
        if not genre_id:
            return None
        
        url = 'http://webservice.recruit.co.jp/hotpepper/genre/v1/'
        params = {
            'key': HOTPEPPER_API_KEY,
            'code': genre_id,
            'format': 'json',
        }
        response = requests.get(url, params)
        data = response.json()
        genre_name = data['results']['genre'][0]['name']

        return genre_name

    def post(self, request):
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        search_range = request.POST.get('search_range')
        genre_id = request.POST.get('genre_id')
        search_budget = request.POST.get('search_budget')

        url = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
        params = {
            'key': HOTPEPPER_API_KEY,
            'lat': latitude,
            'lng': longitude,
            'range': search_range,
            'genre': genre_id,
            'budget': search_budget,
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
        
        genre_name = self.get_genre_name(genre_id=genre_id)

        request.session['restaurants'] = restaurants
        request.session['genre_name'] = genre_name
        request.session['search_range'] = self.SEARCH_RANGE_DICT.get(search_range)
        request.session['search_budget'] = self.SEARCH_BUDGET_DICT.get(search_budget)

        pages = self.get_restaurants_pages(restaurants=restaurants, page=None)

        context = {
            'restaurants': pages,
            'genre_name': genre_name,
            'search_range': self.SEARCH_RANGE_DICT.get(search_range),
            'search_budget': self.SEARCH_BUDGET_DICT.get(search_budget),
        }
        return self.render_to_response(context)
    
    def get(self, request):
        restaurants = request.session.get('restaurants')
        genre_name = request.session.get('genre_name')
        search_range = request.session.get('search_range')
        search_budget = request.session.get('search_budget')
        page = request.GET.get('page')
        pages = self.get_restaurants_pages(restaurants=restaurants, page=page)
        context = {
            'restaurants': pages,
            'genre_name': genre_name,
            'search_range': search_range,
            'search_budget': search_budget,
        }
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
        context["genre_name"] = self.request.session.get('genre_name')
        return context

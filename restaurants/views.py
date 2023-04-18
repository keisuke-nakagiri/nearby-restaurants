import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

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

    def get(self, request):

        if request.GET.get('page'):
            page = request.GET.get('page')
            restaurants = request.session.get('restaurants')
            genre_name = request.session.get('genre_name')
            search_range = request.session.get('search_range')
            search_budget = request.session.get('search_budget')
            paginator = Paginator(restaurants, 20)
            page_obj = paginator.page(page)

            context = {
                'restaurants': page_obj,
                'genre_name': genre_name,
                'search_range': self.SEARCH_RANGE_DICT.get(search_range),
                'search_budget': self.SEARCH_BUDGET_DICT.get(search_budget),
            }

            return self.render_to_response(context)

        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')
        search_range = request.GET.get('search_range')
        genre_id = request.GET.get('genre_id')
        search_budget = request.GET.get('search_budget')
        page = request.GET.get('page', 1)
        per_page = 100
        start = (int(page) - 1) * int(per_page) + 1

        url = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
        params = {
            'key': HOTPEPPER_API_KEY,
            'lat': latitude,
            'lng': longitude,
            'range': search_range,
            'genre': genre_id,
            'budget': search_budget,
            'start': start,
            'count': per_page,
            'format': 'json',
        }

        response = requests.get(url, params)
        data = response.json()
        total_hit_count = data['results']['results_available']
        num_of_searches = (total_hit_count - 1) // per_page + 1

        results = []
        with ThreadPoolExecutor() as executor:
            future_to_restaurant_list = {}
            for i in range(num_of_searches):
                start = i * per_page + 1
                params['start'] = start
                future = executor.submit(requests.get, url, params)
                future_to_restaurant_list[future] = i
            for future in as_completed(future_to_restaurant_list):
                response = future.result()
                results += response.json()['results']['shop']
        
        paginator = Paginator(results, 20)
        page_obj = paginator.get_page(page)

        genre_name = self.get_genre_name(genre_id=genre_id)

        request.session['restaurants'] = results
        request.session['genre_name'] = genre_name
        request.session['search_range'] = search_range
        request.session['search_budget'] = search_budget


        context = {
            'restaurants': page_obj,
            'genre_name': genre_name,
            'search_range': self.SEARCH_RANGE_DICT.get(search_range),
            'search_budget': self.SEARCH_BUDGET_DICT.get(search_budget),
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

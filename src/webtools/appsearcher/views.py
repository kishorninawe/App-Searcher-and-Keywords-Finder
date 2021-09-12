import re

import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from appsearcher.forms import AppSearcherForm


def smart_truncate(content, length=200, suffix='...'):
    if len(content) <= length:
        return content
    return content[:length].rsplit(' ', 1)[0] + suffix


class AppSearchView(View):
    template_name = 'app_searcher.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        form = AppSearcherForm(request.POST)
        if form.is_valid():
            data = {}
            if form.cleaned_data['store'] == 'google':
                package_name = form.cleaned_data['package_name']
                data = self.play_store_search(package_name)
            elif form.cleaned_data['store'] == 'apple':
                app_name = form.cleaned_data['app_name']
                app_id = form.cleaned_data['app_id']
                data = self.app_store_search(app_name, app_id)
            return JsonResponse(data)
        return JsonResponse({'errors': dict(form.errors)})

    @staticmethod
    def play_store_search(package_name):
        try:
            url = 'https://play.google.com/store/apps/details?id=' + package_name
            r = requests.get(url, timeout=300)
            soup = BeautifulSoup(r.text, 'html.parser')
            app_icon_url = soup.find('img', {'class': 'T75of sHb2Xb'}).get('src')
            app_name = soup.find('h1', {'class': 'AHFaub'}).text
            developer_name = soup.find('a', {'class': 'hrTbp R8zArc'}).text
            description_html = soup.find('div', {'class': 'DWPxHb'})
            description = smart_truncate('\n'.join(description_html.strings))
            additional_information = soup.find_all('div', {'class': 'hAyfc'})
            total_downloads = [x.text for x in additional_information][2][8:]
            app_rating = soup.find('div', {'class': 'BHMmbe'}).text
            total_reviews = soup.find('span', {'class': 'EymY4b'}).text[:-6]
            return {
                'app_icon': app_icon_url,
                'app_name': app_name,
                'developer_name': developer_name,
                'description': description,
                'total_downloads': total_downloads,
                'app_rating': app_rating,
                'total_reviews': total_reviews
            }
        except requests.exceptions.ConnectionError:
            return {'error_message': 'Check your internet connection.'}
        except AttributeError:
            return {'error_message': 'App not found.'}

    @staticmethod
    def app_store_search(app_name, app_id):
        app_name = re.sub(r'\'', '', app_name.lower())  # Remove specific character
        app_name_sep = re.split(r'[\s&.-]', app_name)
        app_name_sep = [x for x in app_name_sep if x]
        app_name = '-'.join(app_name_sep)
        try:
            url = 'https://apps.apple.com/in/app/' + app_name + '/id' + app_id
            r = requests.get(url, timeout=300)
            soup = BeautifulSoup(r.text, 'html.parser')
            app_icon_ele = soup.select_one('picture.we-artwork source.we-artwork__source')
            app_icon = ''
            if app_icon_ele:
                app_icon_url = re.search(r'http[s]?://.*?\.webp', app_icon_ele.get('srcset'))
                if app_icon_url:
                    app_icon = app_icon_url.group()

            app_name_raw = soup.find('h1', {'class': 'app-header__title'})
            app_name = [x.strip() for x in app_name_raw.strings][0] if app_name_raw else 'Not found'
            developer_name = soup.find('a', {'class': 'link'})
            description_html = soup.find('div', {'class': 'we-truncate'})
            description = smart_truncate('\n'.join(description_html.strings).strip()) if description_html \
                else 'Not found'
            app_rating = soup.find('span', {'class': 'we-customer-ratings__averages__display'})
            total_reviews = soup.find('div', {'class': 'we-customer-ratings__count small-hide medium-show'})
            return {
                'app_icon': app_icon,
                'app_name': app_name,
                'developer_name': developer_name.text.strip() if developer_name else 'Not found',
                'description': description,
                'app_rating': app_rating.text if app_rating else 'Not found',
                'total_reviews': total_reviews.text[:-8] if total_reviews else 'Not found'
            }
        except requests.exceptions.ConnectionError:
            return {'error_message': 'Check your internet connection.'}
        except AttributeError:
            return {'error_message': 'App not found.'}

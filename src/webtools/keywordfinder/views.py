import re
from urllib.parse import urlparse

import requests
import urllib3
from bs4 import BeautifulSoup
from django.db import IntegrityError
from django.db.models import Sum, Case, When
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from keywordfinder.forms import URLForm
from keywordfinder.models import Keyword, URL

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}


class KeywordFindView(View):
    template_name = 'keyword_finder.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        form = URLForm(request.POST)
        if not form.is_valid():
            return JsonResponse({'errors': dict(form.errors)})

        r = requests.get(form.cleaned_data['url'], verify=False, headers=HEADERS, timeout=300)
        # Clean URL
        url_info = urlparse(r.url, scheme='https')
        url = f'{url_info.scheme}://{url_info.hostname}{url_info.path}{"?" + url_info.query if url_info.query else ""}'

        soup = BeautifulSoup(r.text, 'html.parser')
        get_keywords = soup.find('meta', {'name': re.compile("^keywords$", re.I)})
        get_description = soup.find('meta', {'name': re.compile("^description$", re.I)})
        get_og_description = soup.find('meta', {'name': re.compile("^og:description$", re.I)})

        url_keywords = [
            x.strip().casefold() for x in filter(str.strip, get_keywords.get('content', '').split(','))
        ] if get_keywords else []

        if url_keywords:
            url_keywords.sort(key=str.casefold)

            # Check requested url exists or not
            found_url = URL.objects.filter(url__iregex=r'^(?:https?://)?(?:www\.)?(%s)/?$' % self.sort_urls(url))
            if not found_url:
                url_description = get_description.get('content', '') if get_description else ''
                url_og_description = get_og_description.get('content', '') if get_og_description else ''
                url_instance = URL.objects.create(
                    url=url,
                    description=url_description,
                    og_description=url_og_description
                )
            else:
                url_instance = found_url[0]

            url_keyword_qs = list(Keyword.objects.filter(keyword__in=url_keywords))
            existing_keyword = [x.keyword for x in url_keyword_qs]
            for keyword in set(url_keywords).difference(set(existing_keyword)):
                try:
                    url_keyword_qs.append(Keyword.objects.create(keyword=keyword))
                except IntegrityError:
                    pass  # Fail silently

            url_instance.keyword.add(*url_keyword_qs)

            # If more than 3 keywords match on two urls,
            # show the rest of the keywords from the existing url as 'Recommended keywords'
            # and urls as 'Recommended URLs'.
            # eg. If url present in the database is https://www.dotabuff.com/ with keywords
            # dota 2 stats, dota 2, statistics, dota, guides.
            # Now if the new url entered is https://stratz.com/ which has keywords dota 2 stats, dota 2, statistics.
            # So for https://stratz.com/, the recommended keywords have to be dota, guides.
            # And recommended url is https://www.dotabuff.com/

            # Recommended URLs
            recommended_urls = URL.objects \
                .annotate(tag_count=Sum(Case(When(keyword__in=url_keyword_qs, then=1)))) \
                .filter(tag_count__gte=3) \
                .exclude(id=url_instance.id) \
                .values_list('url', flat=True)

            recommended_urls = sorted(recommended_urls, key=self.sort_urls)

            # Recommended keywords
            recommended_keywords = Keyword.objects \
                .filter(url__url__in=recommended_urls) \
                .exclude(id__in=[x.id for x in url_keyword_qs]) \
                .values_list('keyword', flat=True) \
                .distinct()

            recommended_keywords = sorted(recommended_keywords, key=str.casefold)

            return JsonResponse({
                'url_keywords': url_keywords,
                'recommended_keywords': recommended_keywords,
                'recommended_urls': recommended_urls
            })

        return JsonResponse({'error_message': 'Keyword not found.'})

    @staticmethod
    def sort_urls(url):
        """
        Remove scheme from url and return url start from domain.
        eg. https://www.google.com/ will return google.com
        """
        return re.sub(r'^(?:https?://)?(?:www\.)?|/$', '', url.casefold())

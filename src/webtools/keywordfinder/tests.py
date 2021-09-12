from django.db.models import Sum, Case, When
from django.test import TestCase, Client

from keywordfinder.models import URL, Keyword


class TestPage(TestCase):
    def setUp(self):
        self.client = Client()

    def test_find_keyword(self):
        response = self.client.get('/findkeyword/')
        self.assertEqual(response.status_code, 200)

        # Create existing url
        existing_url = URL.objects.create(
            url='https://www.dotabuff.com/',
            description='Add existing URL',
            og_description='Add existing URL',
        )
        existing_url_keywords = ['dota 2 stats', 'dota 2', 'statistics', 'dota', 'guides']
        existing_url_keyword_qs = [Keyword.objects.create(keyword=x) for x in existing_url_keywords]
        existing_url.keyword.add(*existing_url_keyword_qs)

        # Test for new url
        new_url = URL.objects.create(
            url='https://stratz.com/',
            description='Add new URL',
            og_description='Add new URL',
        )
        new_url_keywords = ['dota 2 stats', 'dota 2', 'statistics']
        new_url_keywords_qs = list(Keyword.objects.filter(keyword__in=new_url_keywords))
        new_url.keyword.add(*new_url_keywords_qs)

        # Recommended URLs
        recommended_urls = URL.objects \
            .annotate(tag_count=Sum(Case(When(keyword__in=new_url_keywords_qs, then=1)))) \
            .filter(tag_count__gte=3) \
            .exclude(id=new_url.id) \
            .values_list('url', flat=True)

        # Recommended keywords
        recommended_keywords = Keyword.objects \
            .filter(url__url__in=recommended_urls) \
            .exclude(id__in=[x.id for x in new_url_keywords_qs]) \
            .values_list('keyword', flat=True) \
            .distinct()

        self.assertEqual(set(recommended_urls), {'https://www.dotabuff.com/'})
        self.assertEqual(set(recommended_keywords), {'dota', 'guides'})

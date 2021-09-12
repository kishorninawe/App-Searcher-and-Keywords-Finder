from django.urls import path

from keywordfinder.views import KeywordFindView

app_name = 'keywordfinder'

urlpatterns = [
    path('', KeywordFindView.as_view(), name='find_keyword'),
]

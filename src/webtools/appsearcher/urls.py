from django.urls import path

from appsearcher.views import AppSearchView

app_name = 'appsearcher'

urlpatterns = [
    path('', AppSearchView.as_view(), name='search_app'),
]

from django.shortcuts import render
from django.http import JsonResponse
from .search import play_store_search, app_store_search


# Create your views here.
def index(request):
	return render(request, "pages/app_searcher.html", None)


def search_app(request):
	store = request.GET['store']
	if store == 'google':
		package_name = request.GET['package_name']
		data = play_store_search(package_name)
		data['store'] = store
		return JsonResponse(data)
	else:
		app_name = request.GET['app_name']
		app_id = request.GET['app_id']
		data = app_store_search(app_name, app_id)
		data['store'] = store
		return JsonResponse(data)

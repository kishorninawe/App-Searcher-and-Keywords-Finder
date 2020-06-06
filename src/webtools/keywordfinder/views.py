from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import FormView
from .keywords import get_keywords_list
from .models import URLKeywordModel, KeywordModel
from .forms import URLForm


class ShowIndex(FormView):
	form_class = URLForm
	template_name = "pages/keyword_finder.html"


def store_keywords_into_database(keywords):
	keywords_qs_list = []
	for keyword in keywords:
		try:
			keyword_qs = KeywordModel.objects.create(keyword=keyword)
			keywords_qs_list.append(keyword_qs)
		except:
			keyword_qs = KeywordModel.objects.get(keyword=keyword)
			keywords_qs_list.append(keyword_qs)
	return keywords_qs_list


def get_data_from_keyword_database(id_list, column):
	values = []
	for id in id_list:
		qs = KeywordModel.objects.filter(id=id).values_list(column, flat=True)
		for value in qs:
			values.append(value)
	return values


def get_data_from_url_database(id_list, column):
	values = []
	for id in id_list:
		qs = URLKeywordModel.objects.filter(id=id).values_list(column,
															   flat=True)
		for value in qs:
			values.append(value)
	return values


def get_keywords(request):
	url = request.GET['url'].rstrip('/')
	result = get_keywords_list(url)
	try:
		url_keywords = result['keywords']
		if url_keywords:
			# store keywords into database
			keyword_id_list = store_keywords_into_database(url_keywords)
			#store url into database
			try:
				url_qs = URLKeywordModel.objects.create(
					url=url,
					description=result['description'],
					ogdescription=result['ogdescription'])
			except:
				url_qs = URLKeywordModel.objects.get(url=url)
			# create relationship between url and keywords
			url_qs.keyword.add(*keyword_id_list)
			original_url_id = url_qs.id

			# get url which have atleast one keyword
			url_id = []
			url_id_list = []
			for keyword_id in keyword_id_list:
				url_qs = URLKeywordModel.objects.filter(
					keyword=keyword_id).values_list('id', flat=True)
				temp_url_id_list = []
				for id in url_qs:
					if id != original_url_id:
						temp_url_id_list.append(id)
						if id not in url_id:
							url_id.append(id)
				url_id_list.append(temp_url_id_list)

			if url_id:
				# get recommended url id
				count = {}
				for id in url_id:
					count[id] = 0
				for url_id in url_id_list:
					for key, value in count.items():
						if key in url_id:
							count[key] = value + 1
				recommended_url_id = [
					key for key, value in count.items() if value > 2
				]

				if recommended_url_id:
					# get rcommended url using url id
					recommended_url = get_data_from_url_database(
						recommended_url_id, 'url')

					# get keywords using keyword id
					keyword_id = get_data_from_url_database(
						recommended_url_id, 'keyword')
					keywords = get_data_from_keyword_database(
						keyword_id, 'keyword')

					# get rcommended keywords using keyword id
					recommended_keywords = []
					for keyword in keywords:
						if keyword not in url_keywords:
							recommended_keywords.append(keyword)
				else:
					return JsonResponse({
						'url_keywords':
						url_keywords,
						'recommended_keywords':
						'No recommended keywords found.',
						'recommended_url':
						'No recommended url found.'
					})
			else:
				return JsonResponse({
					'url_keywords':
					url_keywords,
					'recommended_keywords':
					'No recommended keywords found.',
					'recommended_url':
					'No recommended url found.'
				})
			return JsonResponse({
				'url_keywords': url_keywords,
				'recommended_keywords': recommended_keywords,
				'recommended_url': recommended_url
			})
		else:
			return JsonResponse({'error_message': 'Keyword Not Found.'})
	except KeyError:
		return JsonResponse(result)

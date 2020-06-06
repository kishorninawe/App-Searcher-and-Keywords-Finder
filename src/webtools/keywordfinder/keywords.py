import requests
from bs4 import BeautifulSoup


def get_keywords_list(url):
	try:
		r = requests.get(url)
		html_doc = r.text
		soup = BeautifulSoup(html_doc, 'html.parser')
		get_keywords = soup.find("meta", {"name": "keywords"})
		get_description = soup.find("meta", {"name": "description"})
		get_ogdescription = soup.find("meta", {"property": "og:description"})
		try:
			if get_keywords:
				keywords = list(
					map(lambda x: x.strip(),
						get_keywords.get('content').split(',')))
			else:
				get_keywords = soup.find("meta", {"name": "Keywords"})
				keywords = list(
					map(lambda x: x.strip(),
						get_keywords.get('content').split(',')))
		except AttributeError:
			keywords = False
		try:
			description = get_description.get('content')
		except AttributeError:
			description = ""
		try:
			ogdescription = get_ogdescription.get('content')
		except AttributeError:
			ogdescription = ""
		return {
			'keywords': keywords,
			'description': description,
			'ogdescription': ogdescription
		}
	except requests.exceptions.ConnectionError:
		return {
			'error_message':
			'Url does not exist or check your internet connection.'
		}

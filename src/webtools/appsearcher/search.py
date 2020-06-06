import re
import requests
from bs4 import BeautifulSoup


def smart_truncate(content, length=200, suffix='...'):
	if len(content) <= length:
		return content
	else:
		return content[:length].rsplit(' ', 1)[0] + suffix


def play_store_search(package_name):
	try:
		url = 'https://play.google.com/store/apps/details?id=' + package_name
		r = requests.get(url)
		html_doc = r.text
		soup = BeautifulSoup(html_doc, 'html.parser')
		title = soup.title.text
		app_icon_url = soup.find("img", {"class": "T75of sHb2Xb"})
		app_name = soup.find("h1", {"class": "AHFaub"})
		developer_name = soup.find("a", {"class": "hrTbp R8zArc"})
		description_html = soup.find("div", {"class": "DWPxHb"})
		description_full = '\n'.join(
			list(map(lambda x: x, description_html.strings)))
		description = smart_truncate(description_full)
		additional_information = soup.find_all("div", {"class": "hAyfc"})
		total_downloads = list(map(lambda x: x.text,
								   additional_information))[2]
		app_rating = soup.find("div", {"class": "BHMmbe"})
		total_reviews = soup.find("span", {"class": "EymY4b"})
		return {
			'app_icon': app_icon_url.get('src'),
			'app_name': app_name.text,
			'developer_name': developer_name.text,
			'description': description,
			'total_downloads': total_downloads[8:],
			'app_rating': app_rating.text,
			'total_reviews': total_reviews.text[:-6]
		}
	except requests.exceptions.ConnectionError:
		return {'error_message': 'Check your internet connection.'}
	except AttributeError:
		if title == 'Not Found':
			return {'error_message': 'App Not Found.'}


def app_store_search(app_name, app_id):
	app_name_sep = app_name.lower().split()
	app_name_list = list(
		filter(
			lambda x: bool(re.match("^[A-Za-z0-9-]*$", x)) and not bool(
				re.match("^[\W_]+$", x)), app_name_sep))
	app_name = '-'.join(app_name_list)
	try:
		url = 'https://apps.apple.com/in/app/' + app_name + '/id' + app_id
		r = requests.get(url)
		html_doc = r.text
		soup = BeautifulSoup(html_doc, 'html.parser')
		app_icon_url = soup.find("img", {"class": "we-artwork__image"})
		app_name_raw = soup.find("h1", {"class": "app-header__title"})
		app_name = list(map(lambda x: x.strip(), app_name_raw.strings))
		developer_name = soup.find("a", {"class": "link"})
		description_html = soup.find("div", {"class": "we-truncate"})
		description_full = '\n'.join(
			list(map(lambda x: x, description_html.strings)))
		description = smart_truncate(description_full.strip())
		app_rating = soup.find(
			"span", {"class": "we-customer-ratings__averages__display"})
		total_reviews = soup.find(
			"div",
			{"class": "we-customer-ratings__count small-hide medium-show"})
		return {
			'app_icon': app_icon_url.get('src'),
			'app_name': app_name[0],
			'developer_name': developer_name.text.strip(),
			'description': description,
			'app_rating': app_rating.text,
			'total_reviews': total_reviews.text[:-8]
		}
	except requests.exceptions.ConnectionError:
		return {'error_message': 'Check your internet connection.'}
	except AttributeError:
		return {'error_message': 'App Not Found.'}

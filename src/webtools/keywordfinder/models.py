from django.db import models


# Create your models here.
class KeywordModel(models.Model):
	id = models.AutoField(primary_key=True)
	keyword = models.CharField(unique=True, max_length=100)


class URLKeywordModel(models.Model):
	id = models.AutoField(primary_key=True)
	url = models.CharField(unique=True, max_length=250)
	description = models.CharField(max_length=1000)
	ogdescription = models.CharField(max_length=1000)
	keyword = models.ManyToManyField(KeywordModel, related_name='keyword_name')

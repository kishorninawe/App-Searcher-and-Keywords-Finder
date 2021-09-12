from django.db import models


class Keyword(models.Model):
    keyword = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.keyword


class URL(models.Model):
    url = models.URLField()
    description = models.TextField()
    og_description = models.TextField()
    keyword = models.ManyToManyField(Keyword)

    def __str__(self):
        return self.url

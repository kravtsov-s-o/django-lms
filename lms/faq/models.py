from django.db import models


# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return self.title


class Question(models.Model):
    question = models.CharField(max_length=255, null=False, blank=False)
    answer = models.TextField(null=False, blank=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.question

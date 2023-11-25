from django.db import models
from datetime import datetime


# Create your models here.
class Case(models.Model):
    class CaseType(models.IntegerChoices):
        COMPLETE = 1
        INTERMEDIATE_RECOMMENDATION = 2
        INTERMEDIATE_QUESTION = 3

    name = models.CharField(max_length=255)
    recommendation = models.TextField(blank=True)
    type = models.IntegerField(choices=CaseType.choices)
    create_date = models.DateTimeField("Created on", blank=True)
    update_date = models.DateTimeField("Updated on", blank=True)

    def __str__(self):
        return self.name


class Attr(models.Model):
    priority = models.IntegerField()
    name = models.CharField(max_length=255)
    question = models.TextField(blank=True)

    def __str__(self):
        return self.name


class AttrValue(models.Model):
    case_id = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='case')
    attr_id = models.ForeignKey(Attr, on_delete=models.CASCADE, related_name='attr')
    value = models.CharField(max_length=255, blank=True)

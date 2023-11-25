from django.db import models

# Create your models here.
class Case(models.Model):
    class CaseType(models.IntegerChoices):
        COMPLETE = 1
        INTERMEDIATE_RECOMMENDATION = 2
        INTERMEDIATE_QUESTION = 3

    recommendation = models.TextField()
    type = models.IntegerField(choices=CaseType.choices)


class Attr(models.Model):
    priority = models.IntegerField()
    name = models.CharField(max_length=255)
    question = models.TextField()


class AttrValue(models.Model):
    case_id = models.ForeignKey(Case, on_delete=models.CASCADE)
    attr_id = models.ForeignKey(Attr, on_delete=models.CASCADE)
    value = models.CharField(255)

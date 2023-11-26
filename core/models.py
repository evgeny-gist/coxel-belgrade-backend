from django.db import models
from datetime import datetime


# Create your models here.
class Case(models.Model):
    class CaseType(models.IntegerChoices):
        COMPLETE = 1
        INTERMEDIATE_RECOMMENDATION = 2
        INTERMEDIATE_QUESTION = 3

    name = models.CharField(max_length=255, verbose_name='Имя')
    recommendation = models.TextField(blank=True, verbose_name='Тест рекомендации в MARKDOWN')
    type = models.IntegerField(choices=CaseType.choices, verbose_name='Тип')
    create_date = models.DateTimeField(blank=True, verbose_name='Дата создания')
    update_date = models.DateTimeField(blank=True, verbose_name='Дата обновления')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Кейс'
        verbose_name_plural = 'Кейсы'


class Attr(models.Model):
    priority = models.IntegerField(verbose_name='Приоритет')
    name = models.CharField(max_length=255, verbose_name='Имя')
    question = models.TextField(blank=True, verbose_name='Задаваемый пользователю вопрос')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Атрибут'
        verbose_name_plural = 'Атрибуты'


class AttrValue(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='attr_values', verbose_name='Кейс')
    attr = models.ForeignKey(Attr, on_delete=models.CASCADE, related_name='attr_values', verbose_name='Атрибут')
    value = models.CharField(max_length=255, blank=True, verbose_name='Значение')
    is_any = models.BooleanField(default=False, verbose_name='Нестрогое сравнение')

    def __str__(self):
        return 'Case: ' + self.case.name + ' | ' + self.attr.name + ': ' + (
            str(self.value if not self.is_any else ' {Any variant}'))

    class Meta:
        verbose_name = 'Значение атрибута'
        verbose_name_plural = 'Значения атрибута'

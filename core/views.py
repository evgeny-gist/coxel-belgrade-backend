from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core import serializers

from core.models import Attr, AttrValue, Case


# Create your views here.
@csrf_exempt
def index(request):
    if request.method == "POST":
        return JsonResponse({
            'headers': str(request.headers),
            'post': json.loads(request.body.decode())})


@csrf_exempt
def question(request):
    if request.method == "POST":
        body = json.loads(request.body.decode())
        if not body['attrs']:
            attr = Attr.objects.order_by('priority')[:1].get()
            attr_values = list(AttrValue.objects.filter(attr=attr).values_list('value', flat=True).distinct('value'))

            return JsonResponse({
                'cases': None,
                'question': {
                    'attr_name': attr.name,
                    'question_text': attr.question,
                    'answers': attr_values
                },
                'show_request_form': False,
                'not_strict_recommendation': False
            })

        cases = []  # Здесь все кейсы, у которых совпадает хотя бы один атрибут из запроса
        matched_cases = []
        all_attributes = []
        for body_attr in body['attrs']:
            attr_values = AttrValue.objects.filter(
                Q(value=body_attr['value'], attr__name=body_attr['name']) |
                Q(is_any=True, attr__name=body_attr['name'])
            )
            cases_ids = []
            for attr_value in attr_values:
                cases_ids.append(attr_value.id)

            cases_to_add = Case.objects.filter(pk__in=cases_ids)

            for case in cases_to_add:
                cases.append(case)

        for case in cases:
            skip_case = False
            body_attr_names = []

            for body_attr in body['attrs']:
                body_attr_names.append(body_attr['name'])
                if not case.attr_values.filter(
                        Q(value=body_attr['value'], attr__name=body_attr['name']) |
                        Q(is_any=True, attr__name=body_attr['name'])
                ).exists():
                    skip_case = True

            if skip_case:
                continue

            matched_cases.append(case)
            all_attr_ids = []

            for attr_value_of_case in case.attr_values.all():
                all_attr_ids.append(attr_value_of_case.attr_id)

            attr_priority = None
            try:
                attr_priority = Attr.objects.filter(
                    pk__in=all_attr_ids,
                ).exclude(name__in=body_attr_names).order_by('priority')[:1].get()
            except Exception as e:
                # Если следующей рекомендации нет - не добавляем
                continue

            all_attributes.append(attr_priority)

        if len(all_attributes) == 0:
            return JsonResponse({
                'cases': [
                    {'text': case.recommendation, 'update_date': case.update_date, 'name': case.name}
                    for case in matched_cases],
                'question': None,
                'show_request_form': True,
                'not_strict_recommendation': False
            })
            pass

        sorted_attrs = sorted(all_attributes, key=lambda attr: attr.priority)

        selected_attr = sorted_attrs[0]

        attr_values_values = list(AttrValue.objects.filter(
            attr=selected_attr.id).values_list('value', flat=True).distinct(
            'value'))

        return JsonResponse({
            'cases': None,
            'question': {
                'attr_name': selected_attr.name,
                'question_text': selected_attr.question,
                'answers': attr_values_values
            },
            'show_request_form': False,
            'not_strict_recommendation': False
        })

        # return HttpResponse(str(attr_priority.query))

        # return JsonResponse({
        # 'headers': str(request.headers),
        # 'value': json.loads(request.body.decode())}
        # )

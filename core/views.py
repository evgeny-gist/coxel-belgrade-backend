from datetime import datetime
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core import serializers

from core.models import Attr, AttrValue, Case, RequestAttr, Request, RequestFile


def is_string_empty(string):
    if not string:
        return True
    if not string.strip():
        return True


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
            attr_values = list(AttrValue.objects.filter(
                attr=attr).exclude(value='').values_list('value', flat=True).distinct('value'))

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
        global_cases_ids = []
        matched_cases = []
        all_attributes = []

        # Первое вхождение в цикл рекомендаций
        for body_attr in body['attrs']:
            attr_values = AttrValue.objects.filter(
                Q(value=body_attr['value'], attr__name=body_attr['name']) |
                Q(is_any=True, attr__name=body_attr['name'])
            )
            cases_ids = []
            for attr_value in attr_values:
                cases_ids.append(attr_value.case_id)

            cases_to_add = Case.objects.filter(pk__in=cases_ids)

            for case in cases_to_add:
                if case.id in global_cases_ids:
                    continue
                cases.append(case)
                global_cases_ids.append(case.id)
        print("Cases all", cases)

        # Поиск следующего атрибута
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
                print('Skip case ', case)
                continue

            matched_cases.append(case)
            all_attr_ids = []

            for attr_value_of_case in case.attr_values.all():
                all_attr_ids.append(attr_value_of_case.attr_id)

            try:
                attr_priority_select = Attr.objects.filter(
                    pk__in=all_attr_ids,
                ).exclude(name__in=body_attr_names).order_by('priority')[:1]
                print('AttrPriority query: ', attr_priority_select.query)
                all_attributes.append(attr_priority_select.get())
            except Exception as e:
                print('Error: ', e)
                # Если следующей рекомендации нет - не добавляем
                continue

        # Если нет больше атрибутов(вопросов)
        if len(all_attributes) == 0:
            return JsonResponse({
                'cases': [
                    {'text': case.recommendation, 'update_date': case.update_date, 'name': case.name}
                    for case in matched_cases if not is_string_empty(case.recommendation)],
                'question': None,
                'show_request_form': True,
                'not_strict_recommendation': False
            })

        # Если атрибуты есть - находим с самым высоким приоритетом
        sorted_attrs = sorted(all_attributes, key=lambda attr: attr.priority)

        selected_attr = sorted_attrs[0]

        attr_values_values = list(AttrValue.objects.filter(
            attr=selected_attr.id).exclude(value='').values_list('value', flat=True).distinct('value'))

        # Если есть кейс со строгим совпадением - выводим его в cases
        strict_case = None
        for case in cases:
            if case.attr_values.count() != len(body['attrs']):
                continue
            skip_case = False
            for body_attr in body['attrs']:
                if not case.attr_values.filter(
                        Q(value=body_attr['value'], attr__name=body_attr['name']) |
                        Q(is_any=True, attr__name=body_attr['name'])
                ).exists():
                    skip_case = True
                    break
            if not skip_case:
                strict_case = case
                break

        return JsonResponse({
            'cases': [{
                'text': strict_case.recommendation,
                'update_date': strict_case.update_date,
                'name': strict_case.name}] if strict_case and not is_string_empty(strict_case.recommendation) else None,
            'question': {
                'attr_name': selected_attr.name,
                'question_text': selected_attr.question,
                'answers': attr_values_values
            },
            'show_request_form': False,
            'not_strict_recommendation': False
        })


@csrf_exempt
def fuzzy_recommendation(request):
    if request.method == "POST":
        body = json.loads(request.body.decode())

        cases = []  # Здесь все кейсы, у которых совпадает хотя бы один атрибут из запроса
        global_cases_ids = []
        matched_cases = []

        # Первое вхождение в цикл рекомендаций
        for body_attr in body['attrs']:
            attr_values = AttrValue.objects.filter(
                Q(value=body_attr['value'], attr__name=body_attr['name']) |
                    Q(is_any=True, attr__name=body_attr['name'])
            )
            cases_ids = []
            for attr_value in attr_values:
                cases_ids.append(attr_value.case_id)

            cases_to_add = Case.objects.filter(pk__in=cases_ids)

            for case in cases_to_add:
                if case.id in global_cases_ids:
                    continue
                cases.append(case)
                global_cases_ids.append(case.id)
        print("Cases all", cases)

        # Поиск кейсов нестрого
        for case in cases:
            print('count', case.attr_values.count())

            case_attrs_count = case.attr_values.count()
            attr_value_match_counter = 0
            attr_name_match_counter = 0

            for body_attr in body['attrs']:
                if case.attr_values.filter(
                        Q(value=body_attr['value'], attr__name=body_attr['name']) |
                        Q(is_any=True, attr__name=body_attr['name'])
                ).exists():
                    attr_value_match_counter += 1
                if case.attr_values.filter(attr__name=body_attr['name']).exists():
                    attr_name_match_counter += 1
            if attr_value_match_counter == case_attrs_count - 1 \
                    and attr_name_match_counter == case_attrs_count:
                matched_cases.append(case)

        return JsonResponse({
            'cases': [
                {'text': case.recommendation, 'update_date': case.update_date, 'name': case.name}
                for case in matched_cases if not is_string_empty(case.recommendation)],
            'question': None,
            'show_request_form': True,
            'not_strict_recommendation': False
        })


@csrf_exempt
def upload_request(request):
    if request.method == "POST":
        body = json.loads(request.body.decode())

        user_request = Request(
            topic=body['request_form']['topic'],
            body=body['request_form']['text'],
            user_name=body['request_form']['name'],
            email=body['request_form']['email'],
            additional_contacts=','.join(body['request_form']['additional_contacts'])
        )
        user_request.save()

        for body_attr in body['attrs']:
            request_attr = RequestAttr.objects.create(
                request=user_request,
                name=body_attr['name'],
                value=body_attr['value']
            )
            request_attr.save()

        for file in body['request_form']['files']:
            request_file = RequestFile.objects.create(
                request=user_request,
                url=file
            )
            request_file.save()

        return JsonResponse({'status': 'OK'})

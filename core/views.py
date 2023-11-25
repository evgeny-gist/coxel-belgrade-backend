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
            atrr_values = AttrValue.objects.filter(attr=attr)

            attr_values_response = serializers.serialize('json', atrr_values)

            # todo норм ответ сделать
            # todo сделать distinct
            return JsonResponse({
                'response': [attr.question, attr.name, attr_values_response]
            })


        cases = []
        all_attributes = []
        for body_attr in body['attrs']:
            attr_values = AttrValue.objects.filter(value=body_attr['value'],
                                                   attr__name=body_attr[
                                                       'name'])
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
                        value=body_attr['value'],
                        attr__name=body_attr['name']).exists():
                    skip_case = True

            if skip_case:
                continue

            all_attr_ids = []

            for attr_value_of_case in case.attr_values.all():
                all_attr_ids.append(attr_value_of_case.attr_id)

            attr_priority = Attr.objects.filter(
                pk__in=all_attr_ids,
            ).exclude(name__in=body_attr_names).order_by('priority')[:1].get()

            all_attributes.append(attr_priority)

        sorted_attrs = sorted(all_attributes, key=lambda attr: attr.priority)

        selected_attr = sorted_attrs[0]

        attr_values_values = list(AttrValue.objects.filter(
            attr=selected_attr.id).values_list('value', flat=True).distinct('value'))

        return JsonResponse({
            'question': {
                'attr_name': selected_attr.name,
                'question_text': selected_attr.question,
                'answers': attr_values_values
            }
        })

        # return HttpResponse(str(attr_priority.query))

        # return JsonResponse({
        # 'headers': str(request.headers),
        # 'value': json.loads(request.body.decode())}
        # )

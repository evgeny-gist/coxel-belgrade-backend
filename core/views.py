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
            result = Attr.objects.order_by('priority')[:1]
            return JsonResponse({'value': serializers.serialize('json', result)})
        
        



        # return JsonResponse({
        # 'headers': str(request.headers),
        # 'value': json.loads(request.body.decode())}
        # )
    


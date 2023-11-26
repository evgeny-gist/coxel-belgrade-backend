from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("question", views.question, name="question"),
    path("fuzzy_recommendation", views.fuzzy_recommendation, name="fuzzy_recommendation"),
    path("upload_request", views.upload_request, name="upload_request")
]

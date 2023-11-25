from django.contrib import admin

from .models import *


class CaseAdmin(admin.ModelAdmin):
    list_display = ["name", "update_date"]

    fieldsets = [
        ("Basic",
         {"fields": ['name',
                     'recommendation',
                     'type', ]}),
        ("Date information",
         {"fields": ['create_date',
                     'update_date', ]}),
    ]


admin.site.register(Case, CaseAdmin)
admin.site.register(Attr)
admin.site.register(AttrValue)

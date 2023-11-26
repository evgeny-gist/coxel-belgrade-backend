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


class AttrAdmin(admin.ModelAdmin):
    list_display = ['name', 'priority']
    sortable_by = ['priority']
    ordering = ['-priority']


class AttrValueAdmin(admin.ModelAdmin):
    list_display = ['case', 'attr', 'value', 'is_any']
    sortable_by = ['case', 'attr']
    list_filter = ['case', 'attr']


admin.site.register(Case, CaseAdmin)
admin.site.register(Attr, AttrAdmin)
admin.site.register(AttrValue, AttrValueAdmin)

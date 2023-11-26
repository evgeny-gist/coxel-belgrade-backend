from django.contrib import admin

from .models import *


class CaseAttrValueInline(admin.TabularInline):
    model = AttrValue
    extra = 0


class RequestAttrInline(admin.TabularInline):
    model = RequestAttr
    extra = 0
    readonly_fields = ['name', 'value']
    can_delete = False


class RequestFileInline(admin.TabularInline):
    model = RequestFile
    extra = 0
    readonly_fields = ['url']
    can_delete = False


class CaseAdmin(admin.ModelAdmin):
    list_display = ["name", "update_date"]
    inlines = [CaseAttrValueInline]
    fieldsets = [
        ("Основное",
         {"fields": ['name',
                     'recommendation',
                     'type', ]}),
        ("Дата",
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


class RequestAdmin(admin.ModelAdmin):
    list_display = ["topic", "email", 'create_date']
    readonly_fields = ['create_date']
    inlines = [RequestAttrInline, RequestFileInline]


admin.site.register(Case, CaseAdmin)
admin.site.register(Attr, AttrAdmin)
admin.site.register(AttrValue, AttrValueAdmin)
admin.site.register(Request, RequestAdmin)

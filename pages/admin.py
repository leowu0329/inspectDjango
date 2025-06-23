from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Case

class CaseResource(resources.ModelResource):
    class Meta:
        model = Case
        import_id_fields = ('work_order_number',)  # Using work_order_number as unique identifier
        fields = (
            'inspection_type', 'sale_type', 'customer', 'department', 'date', 'time',
            'work_order_number', 'operator', 'drawing_revision', 'part_number', 'part_name',
            'quantity', 'inspector', 'defect_category', 'defect_description', 'disposition',
            'inspection_hours', 'created_at', 'updated_at'
        )
        export_order = fields

class CaseAdmin(ImportExportModelAdmin):
    resource_class = CaseResource
    list_display = (
        'work_order_number', 'part_name', 'department', 'date', 'inspector',
        'defect_category', 'quantity'
    )
    list_filter = ('department', 'date', 'inspector', 'defect_category', 'inspection_type', 'sale_type')
    search_fields = ('work_order_number', 'part_name', 'part_number', 'customer')
    ordering = ('-date', '-time')

admin.site.register(Case, CaseAdmin)

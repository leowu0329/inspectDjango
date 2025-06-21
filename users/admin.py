from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin
from import_export.formats.base_formats import XLSX
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Profile

# 自訂 Mixin 強制使用 XLSX 格式
class XLSXExportMixin:
    def get_export_formats(self):
        return [XLSX]  # 只返回 XLSX 格式

# CustomUser 資源類別
class CustomUserResource(resources.ModelResource):
    class Meta:
        model = CustomUser
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ['email']
        exclude = ('password',)
        export_order = ('id', 'email', 'username', 'age', 'is_staff', 
                       'is_active', 'date_joined', 'last_login')

# Profile 資源類別
class ProfileResource(resources.ModelResource):
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(CustomUser, 'email')
    )
    
    class Meta:
        model = Profile
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ['user']
        export_order = ('id', 'user', 'role', 'work_area', 'created_at', 'updated_at')

# Profile 內聯管理
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    extra = 0
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# CustomUser 管理員
@admin.register(CustomUser)
class CustomUserAdmin(XLSXExportMixin, UserAdmin, ImportExportModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ['email', 'username', 'age', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'username']
    ordering = ['email']
    inlines = [ProfileInline]
    resource_class = CustomUserResource
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('age',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 
                                  'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'age', 'password1', 'password2'),
        }),
    )
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        if not hasattr(obj, 'profile'):
            Profile.objects.create(user=obj)
        return super().get_inline_instances(request, obj)

# Profile 管理員
@admin.register(Profile)
class ProfileAdmin(XLSXExportMixin, ImportExportModelAdmin):
    list_display = ['user', 'role', 'work_area', 'created_at', 'updated_at']
    list_filter = ['role', 'work_area']
    search_fields = ['user__email', 'user__username', 'work_area']
    resource_class = ProfileResource
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Profile Info', {'fields': ('role', 'work_area')}),
    )

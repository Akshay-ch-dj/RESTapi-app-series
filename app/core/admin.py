from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Recommended Convention for converting strings-> to more user readable
# As it pass through translation engine
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    """
    Custom user admin panel
    """
    ordering = ['id']
    list_display = ['email', 'name']
    # After test_admin --> TEST 2 Fail
    # Adding fieldsets, sections for the fieldsets '()'(4 sections), first one
    # get treated as string('Personal Info'...), then fields for the section
    # Even if one field only seperate it with a comma
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    # After test_admin --> TEST 3 Fail, (error: user name is not specified)
    # customizing add page, adding custom fieldsets, (new user with min. data)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


# Register the models(with modified adminpage)
admin.site.register(models.User, UserAdmin)
# uses the default admin
admin.site.register(models.Tag)

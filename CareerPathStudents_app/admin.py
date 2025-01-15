from django.contrib import admin
from .models import Student


#class StudentAdmin(admin.ModelAdmin):
    # list_display = ['first_name', 'last_name', 'enrollment_year', 'group', 'email']  # Выводим все необходимые поля
    # ordering = ['first_name']  # Сортировка по имени
    # search_fields = ['first_name', 'last_name', 'email']  # Возможность поиска по имени, фамилии и email


#admin.site.register(Student, StudentAdmin)


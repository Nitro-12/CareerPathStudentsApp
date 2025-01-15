from django.db import models
from django.contrib.auth.models import AbstractUser

# Модель для ролей пользователей
class UserRole(models.Model):
    role_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.role_name

# Модель для кастомного пользователя
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_permissions_set',
        blank=True
    )

    def __str__(self):
        return self.username

    def is_teacher(self):
        return self.role and self.role.role_name == "Преподаватель"

    def is_student(self):
        return self.role and self.role.role_name == "Студент"


# Модель для студентов
class Student(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    enrollment_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Мужской', 'Мужской'), ('Женский', 'Женский')], null=True, blank=True)
    group = models.CharField(max_length=50, null=True, blank=True)
    field_of_study = models.CharField(max_length=100, null=True, blank=True)
    course = models.PositiveIntegerField(null=True, blank=True)
    education_level = models.CharField(
        max_length=20,
        choices=[('Бакалавриат', 'Бакалавриат'), ('Магистратура', 'Магистратура'), ('Аспирантура', 'Аспирантура')],
        null=True, blank=True
    )

    def __str__(self):
        return f"  {self.user.last_name} {self.user.first_name} {self.user.middle_name}"


class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, null=True)
    position = models.CharField(max_length=100, null=True)
    subjects = models.TextField()
    gender = models.CharField(max_length=10, choices=[('Мужcкой', 'Мужской'), ('Женский', 'Женский')], null=True, blank=True)
    rank = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position}"


# Модель для рекомендаций
class Recommendation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    reason = models.TextField()

    def __str__(self):
        return f"Рекомендация для {self.student.user.get_full_name()}"


# Модель для достижений студентов
class Achievement(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    description = models.TextField()
    date = models.DateField()
    is_contest = models.BooleanField(default=False)

    def __str__(self):
        return f"Достижение {self.student.user.get_full_name()}: {self.description}"
# Адаптер для предоставления данных из Student и Teacher
class UserAdapter:
    def __init__(self, user_instance):
        self.user_instance = user_instance

    def get_full_name(self):
        # Получение полного имени пользователя
        if isinstance(self.user_instance, Student):
            return f"{self.user_instance.user.last_name} {self.user_instance.user.first_name} {self.user_instance.user.middle_name}"
        elif isinstance(self.user_instance, Teacher):
            return f"{self.user_instance.user.last_name} {self.user_instance.user.first_name} {self.user_instance.user.middle_name}"
        return "Unknown User"

    def get_additional_info(self):
        # Получение дополнительных данных
        if isinstance(self.user_instance, Student):
            return {
                "group": self.user_instance.group,
                "field_of_study": self.user_instance.field_of_study,
                "course": self.user_instance.course,
                "education_level": self.user_instance.education_level,
            }
        elif isinstance(self.user_instance, Teacher):
            return {
                "department": self.user_instance.department,
                "position": self.user_instance.position,
                "subjects": self.user_instance.subjects,
                "rank": self.user_instance.rank,
            }
        return {}


from abc import ABC, abstractmethod

# Интерфейс для адаптера
class TargetInterface(ABC):
    @abstractmethod
    def get_full_name(self):
        pass
    @abstractmethod
    def get_additional_info(self):
        pass

# Реализация адаптера через интерфейс
class UserAdapter(TargetInterface):
    def __init__(self, user_instance):
        self.user_instance = user_instance

    def get_full_name(self):
        if isinstance(self.user_instance, Student):
            return f"{self.user_instance.user.last_name} {self.user_instance.user.first_name} {self.user_instance.user.middle_name}"
        elif isinstance(self.user_instance, Teacher):
            return f"{self.user_instance.user.last_name} {self.user_instance.user.first_name} {self.user_instance.user.middle_name}"
        return "Unknown User"

    def get_additional_info(self):
        if isinstance(self.user_instance, Student):
            return {
                "group": self.user_instance.group,
                "field_of_study": self.user_instance.field_of_study,
                "course": self.user_instance.course,
                "education_level": self.user_instance.education_level,
            }
        elif isinstance(self.user_instance, Teacher):
            return {
                "department": self.user_instance.department,
                "position": self.user_instance.position,
                "subjects": self.user_instance.subjects,
                "rank": self.user_instance.rank,
            }
        return {}

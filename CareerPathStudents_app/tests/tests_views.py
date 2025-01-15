from django.test import TestCase, Client
from django.urls import reverse
from CareerPathStudents_app.models import CustomUser, Student, Teacher, UserRole, Achievement
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()

class ViewsTestCase(TestCase):
    def setUp(self):
        # Создаем роли
        self.student_role = UserRole.objects.create(role_name="Студент")
        self.teacher_role = UserRole.objects.create(role_name="Преподаватель")

        # Создаем пользователей
        self.student_user = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='password123'
        )
        self.student = Student.objects.create(
            user=self.student_user,
            gender='M',
            group='Группа 1',
            field_of_study='Информатика',
            course=2,
            education_level='Бакалавр',
            date_of_birth='2000-01-01',
            enrollment_date='2019-09-01'
        )

        self.teacher_user = User.objects.create_user(
            username='teacher@example.com',
            email='teacher@example.com',
            password='password123'
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            department='ИТ',
            position='Старший преподаватель',
            rank='Кандидат наук',
            gender='M'
        )

        self.client = Client()

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_login_view_success(self):
        response = self.client.post(reverse('login'), {
            'email': 'student@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Перенаправление после входа

    def test_login_view_failure(self):
        response = self.client.post(reverse('login'), {
            'email': 'student@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_student_detail_view(self):
        self.client.login(username='student@example.com', password='password123')
        response = self.client.get(reverse('student_detail', args=[self.student.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.student.group)

    def test_achievement_analytics_api(self):
        Achievement.objects.create(
            student=self.student,
            description='Победа в конкурсе',
            date=datetime.date(2023, 5, 1)
        )
        self.client.login(username='student@example.com', password='password123')
        response = self.client.get(reverse('achievement_analytics_api'), {'student_id': self.student.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')

    def test_register_view(self):
        response = self.client.post(reverse('register'), {
            'firstName': 'Иван',
            'lastName': 'Иванов',
            'middleName': 'Сергеевич',
            'email': 'newstudent@example.com',
            'password': 'password123',
            'role': self.student_role.id,
            'gender': 'M',
            'group': 'Группа 2',
            'field_of_study': 'ИИ',
            'course': 1,
            'education_level': 'Магистр',
            'date_of_birth': '2001-01-01',
            'enrollment_date': '2021-09-01'
        })
        self.assertEqual(response.status_code, 302)  # Перенаправление после успешной регистрации
        self.assertTrue(User.objects.filter(username='newstudent@example.com').exists())




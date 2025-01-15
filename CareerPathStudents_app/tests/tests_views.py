from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from CareerPathStudents_app.models import CustomUser, Student, Teacher, UserRole, Achievement
from django.contrib.auth import get_user_model
from CareerPathStudents_app.views import  student_detail
import datetime
import pandas as pd
from django.contrib.auth.models import User

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

class StudentDetailViewTest(TestCase):
    def setUp(self):
        # Создаем пользователя и студента
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.student = Student.objects.create(user=self.user)

        # Создаем достижения
        Achievement.objects.create(student=self.student, description="Achievement 1", date="2025-01-01", is_contest=True)
        Achievement.objects.create(student=self.student, description="Achievement 2", date="2025-01-10", is_contest=False)
        Achievement.objects.create(student=self.student, description="Achievement 3", date="2025-02-01", is_contest=True)

        # Создаем запрос
        self.factory = RequestFactory()

    def test_student_detail_calculation(self):
        # Создаем GET-запрос
        request = self.factory.get(f'/students/{self.student.id}/')
        request.user = self.user
        # Вызываем представление
        response = student_detail(request, self.student.id)
        # Проверяем статус ответа
        self.assertEqual(response.status_code, 200)

        # Рендерим шаблон и извлекаем данные контекста через прямой вызов логики
        student = self.student
        achievements = Achievement.objects.filter(student=student).values('description', 'date', 'is_contest')
        df = pd.DataFrame(list(achievements))

        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.to_period('M')
            monthly_counts = df.groupby('month').size()
            average_per_month = monthly_counts.mean()
            contest_count = df['is_contest'].sum()
            total_count = len(df)
            success_rate = (contest_count / total_count * 100) if total_count > 0 else 0
        else:
            average_per_month = 0
            success_rate = 0

        self.assertEqual(round(average_per_month, 2), 1.5)
        self.assertEqual(round(success_rate, 2), 66.67)







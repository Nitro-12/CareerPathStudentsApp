from unittest.mock import patch, MagicMock
from django.test import TestCase
from CareerPathStudents_app.models import CustomUser, UserRole, Student, Teacher, Recommendation, Achievement
from django.utils import timezone


class UserRoleTestCase(TestCase):
    @patch('CareerPathStudents_app.models.UserRole.objects.create')
    def test_create_user_role(self, mock_create):
        mock_role = MagicMock(role_name="Преподаватель")
        mock_create.return_value = mock_role

        role = UserRole.objects.create(role_name="Преподаватель")
        self.assertEqual(role.role_name, "Преподаватель")
        mock_create.assert_called_once_with(role_name="Преподаватель")


class CustomUserTestCase(TestCase):
    @patch('CareerPathStudents_app.models.CustomUser.objects.create_user')
    def test_create_custom_user(self, mock_create_user):
        mock_user = MagicMock(
            username="testuser",
            email="testuser@example.com",
            check_password=lambda x: x == "password123",
        )
        mock_user.role.role_name = "Студент"
        mock_create_user.return_value = mock_user

        user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            role=MagicMock(role_name="Студент"),
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@example.com")
        self.assertTrue(user.check_password("password123"))
        self.assertEqual(user.role.role_name, "Студент")
        mock_create_user.assert_called_once()


class StudentTestCase(TestCase):
    @patch('CareerPathStudents_app.models.Student.objects.create')
    def test_create_student(self, mock_create):
        mock_student = MagicMock(
            user=MagicMock(first_name="Student"),
            group="Группа 1",
        )
        mock_create.return_value = mock_student

        student = Student.objects.create(
            user=MagicMock(first_name="Student"),
            date_of_birth="2000-01-01",
            enrollment_date="2020-09-01",
            gender="Мужской",
            group="Группа 1",
            field_of_study="Информатика",
        )
        self.assertEqual(student.user.first_name, "Student")
        self.assertEqual(student.group, "Группа 1")
        mock_create.assert_called_once()


class TeacherTestCase(TestCase):
    @patch('CareerPathStudents_app.models.Teacher.objects.create')
    def test_create_teacher(self, mock_create):
        mock_teacher = MagicMock(position="Профессор")
        mock_create.return_value = mock_teacher

        teacher = Teacher.objects.create(
            user=MagicMock(),
            department="Кафедра ИТ",
            position="Профессор",
            subjects="Программирование, Алгоритмы",
        )
        self.assertEqual(teacher.position, "Профессор")
        mock_create.assert_called_once()


class RecommendationTestCase(TestCase):
    @patch('CareerPathStudents_app.models.Recommendation.objects.create')
    def test_create_recommendation(self, mock_create):
        mock_recommendation = MagicMock(reason="Рекомендуется для улучшения навыков программирования")
        mock_create.return_value = mock_recommendation

        recommendation = Recommendation.objects.create(
            student=MagicMock(),
            reason="Рекомендуется для улучшения навыков программирования",
        )
        self.assertEqual(recommendation.reason, "Рекомендуется для улучшения навыков программирования")
        mock_create.assert_called_once()


class AchievementTestCase(TestCase):
    @patch('CareerPathStudents_app.models.Achievement.objects.create')
    @patch('django.utils.timezone.now', return_value=timezone.now())
    def test_create_achievement(self, mock_now, mock_create):
        mock_achievement = MagicMock(description="Завершение курса по Python")
        mock_create.return_value = mock_achievement

        achievement = Achievement.objects.create(
            student=MagicMock(),
            description="Завершение курса по Python",
            date=mock_now.return_value,
        )
        self.assertEqual(achievement.description, "Завершение курса по Python")
        mock_create.assert_called_once()

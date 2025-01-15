from django.test import TestCase
from CareerPathStudents_app.models import CustomUser, UserRole, Student, Teacher,  Recommendation, Achievement
from django.utils import timezone


class UserRoleTestCase(TestCase):
    def test_create_user_role(self):
        role = UserRole.objects.create(role_name="Преподаватель")
        self.assertEqual(role.role_name, "Преподаватель")


class CustomUserTestCase(TestCase):
    def test_create_custom_user(self):
        role = UserRole.objects.create(role_name="Студент")
        user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            role=role
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@example.com")
        self.assertTrue(user.check_password("password123"))
        self.assertEqual(user.role.role_name, "Студент")

    def test_is_teacher_method(self):
        role = UserRole.objects.create(role_name="Преподаватель")
        user = CustomUser.objects.create_user(
            username="teacheruser",
            email="teacheruser@example.com",
            password="password123",
            first_name="Teacher",
            last_name="User",
            role=role
        )
        self.assertTrue(user.is_teacher())
        self.assertFalse(user.is_student())

class StudentTestCase(TestCase):
    def test_create_student(self):
        role = UserRole.objects.create(role_name="Студент")
        user = CustomUser.objects.create_user(
            username="studentuser",
            email="studentuser@example.com",
            password="password123",
            first_name="Student",
            last_name="User",
            role=role
        )
        student = Student.objects.create(user=user, date_of_birth="2000-01-01", enrollment_date="2020-09-01",
                                         gender="Мужской", group="Группа 1", field_of_study="Информатика")
        self.assertEqual(student.user.first_name, "Student")
        self.assertEqual(student.group, "Группа 1")


class TeacherTestCase(TestCase):
    def test_create_teacher(self):
        role = UserRole.objects.create(role_name="Преподаватель")
        user = CustomUser.objects.create_user(
            username="teacheruser",
            email="teacheruser@example.com",
            password="password123",
            first_name="Teacher",
            last_name="User",
            role=role
        )
        teacher = Teacher.objects.create(user=user, department="Кафедра ИТ", position="Профессор",
                                         subjects="Программирование, Алгоритмы")
        self.assertEqual(teacher.position, "Профессор")


class RecommendationTestCase(TestCase):
    def test_create_recommendation(self):
        role = UserRole.objects.create(role_name="Студент")
        user = CustomUser.objects.create_user(
            username="studentuser",
            email="studentuser@example.com",
            password="password123",
            first_name="Student",
            last_name="User",
            role=role
        )
        student = Student.objects.create(user=user, date_of_birth="2000-01-01", enrollment_date="2020-09-01")
        recommendation = Recommendation.objects.create(student=student, reason="Рекомендуется для улучшения "
                                                                               "навыков программирования")
        self.assertEqual(recommendation.reason, "Рекомендуется для улучшения навыков программирования")


class AchievementTestCase(TestCase):
    def test_create_achievement(self):
        role = UserRole.objects.create(role_name="Студент")
        user = CustomUser.objects.create_user(
            username="studentuser",
            email="studentuser@example.com",
            password="password123",
            first_name="Student",
            last_name="User",
            role=role
        )
        student = Student.objects.create(user=user, date_of_birth="2000-01-01", enrollment_date="2020-09-01")
        achievement = Achievement.objects.create(student=student, description="Завершение курса по Python", date=timezone.now())
        self.assertEqual(achievement.description, "Завершение курса по Python")




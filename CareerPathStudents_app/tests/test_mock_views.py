from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from CareerPathStudents_app.models import CustomUser, Student, Achievement, Recommendation
from CareerPathStudents_app.views import student_detail

class GenerateRecommendationsTests(TestCase):
    def setUp(self):
        # Создаем пользователя и студента
        self.user = CustomUser.objects.create_user(username="testuser", password="password123")
        self.student = Student.objects.create(
            user=self.user,
            gender='М',
            group='201',
            field_of_study='Физика',
            course=2,
            education_level='Бакалавриат'
        )
        # Создаем достижения для студента
        Achievement.objects.create(
            student=self.student,
            description="Участие в хакатоне",
            date="2025-01-05",
            is_contest=True
        )
        Achievement.objects.create(
            student=self.student,
            description="Посещение конференции",
            date="2025-02-10",
            is_contest=False
        )
        self.url = reverse('generate_recommendations')

    def test_generate_recommendations_no_achievements(self):
        # Удаляем все достижения
        Achievement.objects.all().delete()

        # Логиним пользователя
        self.client.login(username="testuser", password="password123")

        response = self.client.get(self.url)

        # Проверяем статус ответа
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {"error": "У студента нет достижений для анализа."})

    @patch('django.core.cache.cache.get')
    @patch('django.core.cache.cache.set')
    @patch('sklearn.cluster.KMeans.fit_predict')
    def test_generate_recommendations_success(self, mock_fit_predict, mock_cache_set, mock_cache_get):
        # Мокаем кластеризацию
        mock_fit_predict.return_value = [0, 0]
        mock_cache_get.return_value = None
        mock_cache_set.return_value = None

        # Логиним пользователя
        self.client.login(username="testuser", password="password123")

        response = self.client.get(self.url)

        # Проверяем статус ответа
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Популярный тип")
        self.assertTrue(Recommendation.objects.filter(student=self.student).exists())

@patch('CareerPathStudents_app.models.Student')
@patch('CareerPathStudents_app.models.Achievement')
def test_student_detail_mock(achievement_mock, student_mock):
    # Настраиваем мок-объекты
    student_mock.objects.get.return_value = MagicMock(id=1, name="Mock Student")
    achievement_mock.objects.filter.return_value.values.return_value = [
        {'description': 'Achievement 1', 'date': '2025-01-01', 'is_contest': True},
        {'description': 'Achievement 2', 'date': '2025-01-15', 'is_contest': False},
        {'description': 'Achievement 3', 'date': '2025-02-01', 'is_contest': True},
    ]

    # Создаем запрос
    factory = RequestFactory()
    request = factory.get('/mock_student_detail/')
    request.user = MagicMock()

    # Вызываем представление
    response = student_detail(request, 1)

    # Проверяем контекст
    assert response.status_code == 200
    assert response.context_data['average_per_month'] == 2.0  # Проверяем расчет
    assert response.context_data['success_rate'] == 66.67  # Проверяем успешность

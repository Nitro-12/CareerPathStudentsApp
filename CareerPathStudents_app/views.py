from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.db.models.functions import Concat
from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, Teacher, Achievement, Recommendation, CustomUser, UserRole
from django.http import JsonResponse, HttpResponse
import matplotlib
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from collections import Counter
from django.db.models import Q, Value
from django.contrib import messages
from io import BytesIO
from rest_framework.decorators import api_view
from django.views.generic.detail import DetailView
import pandas as pd
import matplotlib.pyplot as plt
from django.http import JsonResponse

# Главная страница
def index(request):
    return render(request, 'index.html')


# Форма для логина с использованием email
class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Пароль"
    )


class StudentDetailView(DetailView):
    model = Student
    template_name = 'student_detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        # Получаем базовый контекст
        context = super().get_context_data(**kwargs)
        # Добавляем достижения студента
        context['achievements'] = Achievement.objects.filter(student=self.object)
        # Проверяем, является ли пользователь преподавателем
        context['is_teacher'] = self.request.user.groups.filter(name='Преподаватели').exists()
        return context

@login_required
def student_detail(request, student_id):
    # Получаем объект студента по id
    student = get_object_or_404(Student, id=student_id)

    # Получаем достижения студента
    achievements = Achievement.objects.filter(student=student).values('description', 'date', 'is_contest')

    # Преобразуем данные в DataFrame
    df = pd.DataFrame(list(achievements))

    # Проверяем, есть ли данные
    if not df.empty:
        # Преобразуем колонку `date` в формат datetime
        df['date'] = pd.to_datetime(df['date'])

        # Группируем по месяцам и считаем количество достижений
        df['month'] = df['date'].dt.to_period('M')
        monthly_counts = df.groupby('month').size()

        # Рассчитываем среднее количество достижений в месяц
        average_per_month = monthly_counts.mean()

        # Рассчитываем успешность студента (процент достижений, связанных с конкурсами)
        contest_count = df['is_contest'].sum()  # Количество достижений, связанных с конкурсами
        total_count = len(df)
        success_rate = (contest_count / total_count * 100) if total_count > 0 else 0
    else:
        # Если данных нет, устанавливаем значения по умолчанию
        average_per_month = 0
        success_rate = 0
    print("Среднее количество достижений в месяц:", average_per_month)
    print("Успешность студента (участие в конкурсах):", success_rate)

    # Передаём данные в шаблон
    return render(request, 'student_detail.html', {
        'student': student,
        'achievements': achievements,
        'average_per_month': round(average_per_month, 2),
        'success_rate': round(success_rate, 2),
    })



@api_view(['GET'])
def achievement_analytics_api(request):
    student_id = request.GET.get('student_id')
    if not student_id:
        return JsonResponse({"error": "Не указан student_id"}, status=400)
    # Получаем достижения для конкретного студента
    achievements = Achievement.objects.filter(student_id=student_id).values("description", "date")
    matplotlib.use('Agg')
    # Преобразуем данные в DataFrame
    df = pd.DataFrame(list(achievements))

    # Проверяем, есть ли данные
    if df.empty:
        return JsonResponse({"error": "Нет данных для анализа."}, status=404)

    # Преобразуем даты и группируем достижения по месяцам
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    achievement_counts = df.groupby('month').size()

    # Построение графика достижений по времени
    plt.figure(figsize=(10, 5))
    achievement_counts.plot(kind='bar', color='skyblue')
    plt.title('Количество достижений по месяцам')
    plt.xlabel('Месяц')
    plt.ylabel('Количество достижений')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Сохранение графика в буфер
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()  # Закрываем график
    buffer.seek(0)

    return HttpResponse(buffer, content_type='image/png')


def login_view(request):
    if request.method == "POST":
        form = EmailLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)

                # Перенаправление в зависимости от роли
                if user.is_teacher():
                    return redirect('teacher_dashboard')  # Перенаправляем преподавателя
                else:
                    return redirect('dashboard')  # Студент попадает в личный кабинет
            else:
                messages.error(request, 'Неправильный email или пароль')
    else:
        form = EmailLoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def generate_recommendations(request):
    # Получаем текущего студента
    student = Student.objects.get(user=request.user)

    # Получаем достижения студента
    achievements = Achievement.objects.filter(student=student).values('description', 'date')

    if not achievements:
        return JsonResponse({"error": "У студента нет достижений для анализа."}, status=400)

    # Преобразуем данные в DataFrame
    df = pd.DataFrame(list(achievements))

    # Преобразуем дату в datetime и создаем дополнительные признаки (например, месяц)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month

    # Создаем бинарный признак "is_contest" на основе описания (если в описании упоминаются слова 'конкурс', 'олимпиада', 'хакатон', 'турнир', 'конференция', 'чемпионат' и т.д.)
    contest_keywords = ['конкурс', 'олимпиада', 'хакатон', 'турнир', 'конференция', 'чемпионат', 'семинар', 'выставка',
                        'форум']

    # Применяем фильтрацию по ключевым словам
    df['is_contest'] = df['description'].apply(
        lambda x: 1 if any(keyword in x.lower() for keyword in contest_keywords) else 0)

    # Подготовка данных для кластеризации
    features = df[['month', 'is_contest']].values  # Включаем только признаки для кластеризации

    # Масштабируем данные
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # Применяем KMeans для кластеризации студентов
    kmeans = KMeans(n_clusters=3, random_state=42)  # Количество кластеров можно настроить
    df['cluster'] = kmeans.fit_predict(scaled_features)

    # Получаем кластер текущего студента
    student_cluster = None
    for achievement in achievements:
        cluster = df[df['description'] == achievement['description']]['cluster'].values
        if cluster.size > 0:
            student_cluster = cluster[0]
            break  # Выход из цикла после нахождения первого совпадения

    if student_cluster is None:
        return JsonResponse({"error": "Не удалось определить кластер студента."}, status=400)

    # Рекомендуем достижения студентов из того же кластера
    recommendations = df[df['cluster'] == student_cluster]

    # Извлекаем первое слово из описания для определения типа
    first_words = recommendations['description'].apply(lambda x: x.split()[0].lower())

    # Находим наиболее часто встречающееся первое слово (тип достижения)
    most_common_type = Counter(first_words).most_common(1)

    if most_common_type:
        most_common_type = most_common_type[0][0]  # Извлекаем наиболее частое слово (тип)

        # Сохраняем рекомендацию с наиболее популярным типом достижения
        recommendation_text = f"Популярный тип: {most_common_type}"

        # Сохраняем уникальную рекомендацию
        if not Recommendation.objects.filter(student=student, reason=recommendation_text).exists():
            Recommendation.objects.create(student=student, reason=recommendation_text)
            return JsonResponse({"recommendations": [{"reason": recommendation_text}]}, status=200)

        return JsonResponse({"error": "Рекомендация уже была добавлена."}, status=400)
    else:
        return JsonResponse({"error": "Не удалось найти популярный тип достижения."}, status=400)


def register_view(request):
    if request.method == 'POST':
        # Получаем данные из формы
        first_name = request.POST['firstName']
        last_name = request.POST['lastName']
        middle_name = request.POST['middleName']
        email = request.POST['email']
        password = request.POST['password']
        role_id = request.POST['role']

        # Создаем username, например, используя email
        username = email  # или можно генерировать другое имя пользователя

        # Получаем роль
        role = UserRole.objects.get(id=role_id)

        # Создаем пользователя с добавлением username
        user = CustomUser.objects.create_user(username=username, email=email, password=password, last_name=last_name, first_name=first_name, middle_name=middle_name)
        user.role = role
        user.save()

        # Добавляем студента или преподавателя в зависимости от роли
        if role.role_name == "Студент":
            student = Student(
                user=user,
                gender=request.POST.get('gender'),
                group=request.POST.get('group'),
                field_of_study=request.POST.get('field_of_study'),
                course=request.POST.get('course'),
                education_level=request.POST.get('education_level'),
                date_of_birth=request.POST.get('date_of_birth'),
                enrollment_date=request.POST.get('enrollment_date')
            )
            student.save()
            dashboard_url = 'dashboard'  # URL для ЛК студента

        elif role.role_name == "Преподаватель":
            teacher = Teacher(
                user=user,
                department=request.POST.get('department'),
                position=request.POST.get('position'),
                rank=request.POST.get('rank'),
                subjects=request.POST.get('subjects'),
                gender=request.POST.get('gender_teacher')
            )
            teacher.save()
            dashboard_url = 'teacher_dashboard'  # URL для ЛК преподавателя

        # Авторизуем пользователя
        login(request, user)

        # Перенаправляем на соответствующий ЛК
        return redirect(dashboard_url)

    # Получаем все роли для отображения в выпадающем списке
    roles = UserRole.objects.all()

    return render(request, 'register.html', {'roles': roles})


@login_required
def teacher_dashboard(request):
    teacher = Teacher.objects.get(user=request.user)
    students = Student.objects.all()  # Можно добавить фильтрацию по кафедре

    return render(request, 'teacher_dashboard.html', {'teacher': teacher, 'students': students})


@login_required
def recommendations_view(request):
    student = Student.objects.get(user=request.user)
    recommendations = Recommendation.objects.filter(student=student)
    return render(request, 'recommendations.html', {
        "recommendations": recommendations,
        "student": student
    })


# Личный кабинет студента
@login_required
def student_dashboard(request):
    try:
        student = Student.objects.get(user=request.user)
        achievements = Achievement.objects.filter(student=student)
        recommendations = Recommendation.objects.filter(student=student)

        context = {
            "student_name": f"{student.user.last_name} {student.user.first_name} {student.user.middle_name}",
            "email": student.user.email,
            "achievements": achievements,
            "recommendations": recommendations,
        }
        return render(request, 'dashboard.html', context)
    except Student.DoesNotExist:
        return render(request, 'dashboard.html', {"error": "Студент не найден."})

@login_required
# Список студентов
def student_list(request):
    students = Student.objects.all()

    selected_group = request.GET.get('group', '')
    selected_field_of_study = request.GET.get('field_of_study', '')
    selected_course = request.GET.get('course', '')
    selected_education_level = request.GET.get('education_level', '')

    if selected_group:
        students = students.filter(group=selected_group)
    if selected_field_of_study:
        students = students.filter(field_of_study=selected_field_of_study)
    if selected_course:
        students = students.filter(course=selected_course)
    if selected_education_level:
        students = students.filter(education_level=selected_education_level)

    groups = Student.objects.values_list('group', flat=True).distinct()
    fields_of_study = Student.objects.values_list('field_of_study', flat=True).distinct()
    courses = Student.objects.values_list('course', flat=True).distinct()
    education_levels = Student.objects.values_list('education_level', flat=True).distinct()

    context = {
        'students': students,
        'groups': groups,
        'fields_of_study': fields_of_study,
        'courses': courses,
        'education_levels': education_levels,
        'selected_group': selected_group,
        'selected_field_of_study': selected_field_of_study,
        'selected_course': selected_course,
        'selected_education_level': selected_education_level,
    }
    return render(request, 'students.html', context)


@login_required
def add_achievement(request):
    if request.method == "POST":
        description = request.POST.get("description")
        date = request.POST.get("date")

        # Получаем текущего студента
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            return render(request, 'dashboard.html', {"error": "Студент не найден."})

        # Создаем новое достижение
        Achievement.objects.create(student=student, description=description, date=date)

        # Перенаправляем обратно на страницу личного кабинета
        return redirect('dashboard')
    else:
        return redirect('dashboard')


@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher():
        return render(request, 'error.html', {'message': 'Access denied'})

    # Получаем преподавателя
    teacher = Teacher.objects.get(user=request.user)

    # Получаем всех студентов (по желанию, добавьте фильтрацию)
    students = Student.objects.all()

    return render(request, 'teacher_dashboard.html', {'teacher': teacher, 'students': students})

@login_required
def student_search(request):
    # Получение параметров фильтра из запроса
    selected_group = request.GET.get('group', '')
    selected_field_of_study = request.GET.get('field_of_study', '')
    selected_course = request.GET.get('course', '')
    selected_education_level = request.GET.get('education_level', '')
    query = request.GET.get('query', '')

    # Список всех студентов
    students = Student.objects.all()

    # Применение фильтров только если параметры указаны
    if selected_group:
        students = students.filter(group=selected_group)
    if selected_field_of_study:
        students = students.filter(field_of_study=selected_field_of_study)
    if selected_course:
        students = students.filter(course=selected_course)
    if selected_education_level:
        students = students.filter(education_level=selected_education_level)
    if query:
        # Подключаем Concat для объединения полей в одну строку
        students = students.annotate(
            full_name=Concat('user__last_name', Value(' '), 'user__first_name', Value(' '), 'user__middle_name')
        ).filter(
            Q(full_name__icontains=query) |  # Полное ФИО
            Q(user__last_name__icontains=query) |  # Только фамилия
            Q(user__first_name__icontains=query) |  # Только имя
            Q(user__middle_name__icontains=query)  # Только отчество
        )

    # Список значений для фильтров из БД
    groups = Student.objects.values_list('group', flat=True).distinct()
    fields_of_study = Student.objects.values_list('field_of_study', flat=True).distinct()
    courses = Student.objects.values_list('course', flat=True).distinct()
    education_levels = Student.objects.values_list('education_level', flat=True).distinct()

    # Передача данных в контекст
    context = {
        'students': students,
        'query': query,
        'groups': groups,
        'fields_of_study': fields_of_study,
        'courses': courses,
        'education_levels': education_levels,
        'selected_group': selected_group,
        'selected_field_of_study': selected_field_of_study,
        'selected_course': selected_course,
        'selected_education_level': selected_education_level,
    }
    return render(request, 'students.html', context)
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import EmployeeProfile


class EmployeeDeskValidationTestCase(TestCase):
    def setUp(self):
        """Создаем базовых пользователей для привязки к профилям."""
        self.user_qa = User.objects.create_user(username="qa_user", password="password123")
        self.user_backend = User.objects.create_user(username="backend_user", password="password123")
        self.user_frontend = User.objects.create_user(username="frontend_user", password="password123")
        self.user_other = User.objects.create_user(username="other_user", password="password123")

    def test_allowed_seating_separated_desks(self):
        """Проверка: Разработчик и тестировщик могут сидеть далеко друг от друга (например, через стол)."""
        # Сажаем бэкендера за 1-й стол
        backend_emp = EmployeeProfile.objects.create(
            user=self.user_backend,
            first_name="Иван",
            last_name="Иванов",
            gender="M",
            role="backend",
            desk_number=1
        )
        # Сажаем тестировщика за 3-й стол (между ними свободный 2-й)
        try:
            qa_emp = EmployeeProfile.objects.create(
                user=self.user_qa,
                first_name="Петр",
                last_name="Петров",
                gender="M",
                role="qa",
                desk_number=3
            )
        except ValidationError:
            self.fail("ValidationError была брошена ошибочно! Столы 1 и 3 не являются соседними.")

    def test_forbidden_seating_qa_next_to_backend(self):
        """Проверка: Тестировщик НЕ может сесть за стол, соседний с бэкендером."""
        # Сначала сажаем бэкендера за стол №2
        EmployeeProfile.objects.create(
            user=self.user_backend,
            first_name="Иван",
            last_name="Иванов",
            gender="M",
            role="backend",
            desk_number=2
        )

        # Пытаемся посадить тестировщика за соседний стол №3
        qa_emp = EmployeeProfile(
            user=self.user_qa,
            first_name="Петр",
            last_name="Петров",
            gender="M",
            role="qa",
            desk_number=3
        )
        
        # Ожидаем, что метод save() вызовет ValidationError
        with self.assertRaises(ValidationError) as context:
            qa_emp.save()
            
        # Проверяем, что ошибка привязана именно к полю desk_number
        self.assertIn('desk_number', context.exception.message_dict)

    def test_forbidden_seating_frontend_next_to_qa(self):
        """Проверка: Фронтендер НЕ может сесть за стол, соседний с тестировщиком."""
        # Сначала сажаем тестировщика за стол №5
        EmployeeProfile.objects.create(
            user=self.user_qa,
            first_name="Петр",
            last_name="Петров",
            gender="M",
            role="qa",
            desk_number=5
        )

        # Пытаемся посадить фронтендера за соседний стол №4
        frontend_emp = EmployeeProfile(
            user=self.user_frontend,
            first_name="Анна",
            last_name="Сидорова",
            gender="F",
            role="frontend",
            desk_number=4
        )
        
        with self.assertRaises(ValidationError) as context:
            frontend_emp.save()
            
        self.assertIn('desk_number', context.exception.message_dict)

    def test_allowed_seating_other_roles(self):
        """Проверка: Сотрудники с ролью 'other' (другое) могут сидеть рядом с кем угодно."""
        # Сажаем тестировщика за стол №10
        EmployeeProfile.objects.create(
            user=self.user_qa,
            first_name="Петр",
            last_name="Петров",
            gender="M",
            role="qa",
            desk_number=10
        )

        # Сажаем сотрудника с ролью 'other' за соседний стол №11 — это должно быть разрешено
        try:
            other_emp = EmployeeProfile.objects.create(
                user=self.user_other,
                first_name="Ольга",
                last_name="Кузнецова",
                gender="F",
                role="other",
                desk_number=11
            )
        except ValidationError:
            self.fail("ValidationError не должна бросаться для сотрудников с ролью 'other'.")

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Profile
from .selectors import UserSelector
from .services import UserService

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_has_role_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com", password="adminpass123"
        )
        self.assertTrue(user.has_role("any_role"))

    def test_profile_auto_created(self):
        user = User.objects.create_user(
            email="profile@example.com", password="testpass123"
        )
        self.assertTrue(hasattr(user, "profile"))
        self.assertIsInstance(user.profile, Profile)


class UserSelectorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="sel@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )
        self.user.profile.first_name = "John"
        self.user.profile.last_name = "Doe"
        self.user.profile.save()

    def test_list_users_returns_list_of_dicts(self):
        users = UserSelector.list_users()
        self.assertIsInstance(users, list)
        self.assertGreater(len(users), 0)
        user_dict = users[0]
        self.assertIn("email", user_dict)
        self.assertIn("full_name", user_dict)

    def test_user_exists(self):
        self.assertTrue(UserSelector.user_exists("sel@example.com"))
        self.assertFalse(UserSelector.user_exists("nobody@example.com"))


class UserServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="service@example.com", password="testpass123"
        )

    def test_register_user_success(self):
        new_user = UserService.register_user(
            email="new@example.com",
            password="testpass123",
            first_name="Bob",
            last_name="Builder",
        )
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.email, "new@example.com")

    def test_register_user_duplicate_raises(self):
        with self.assertRaises(ValueError):
            UserService.register_user(
                email="service@example.com", password="testpass123"
            )

    def test_toggle_active(self):
        self.assertTrue(self.user.is_active)
        new_status = UserService.toggle_active(str(self.user.id))
        self.user.refresh_from_db()
        self.assertFalse(new_status)
        self.assertFalse(self.user.is_active)

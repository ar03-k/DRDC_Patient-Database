from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Patient


class PatientAuthenticationTests(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            name='Test Patient',
            age=35,
            gender='O',
            phone='5551234567',
            date_of_diagnosis='2025-01-01',
        )

    def test_patient_pages_redirect_anonymous_users_to_login(self):
        paths = [
            reverse('add_patient'),
            reverse('addpatient_success'),
            reverse('view_patients'),
            reverse('patient_detail', kwargs={'pk': self.patient.pk}),
            reverse('edit_patient', kwargs={'pk': self.patient.pk}),
            reverse('add_visit', kwargs={'pk': self.patient.pk}),
            reverse('delete_patient', kwargs={'pk': self.patient.pk}),
        ]

        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertRedirects(
                    response,
                    f'{reverse("login")}?next={path}',
                    fetch_redirect_response=False,
                )

    def test_authenticated_user_can_view_patient_list(self):
        user_model = get_user_model()
        user_model.objects.create_user(username='clinic-staff', password='test-password')
        self.client.login(username='clinic-staff', password='test-password')

        response = self.client.get(reverse('view_patients'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.patient.name)

    def test_login_page_is_available_to_anonymous_users(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Staff log in')

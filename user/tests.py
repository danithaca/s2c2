from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from user.models import UserProfile


class UserTest(TestCase):

    # test cases:
    # signup:
    # 1. without invitation code, cannot signup
    # 2. normal signup

    # 3. update profile
    # 4. update picture

    # 5. change role
    # 6 .change centers

    def test_signup(self):
        response = self.client.get(reverse('user:signup'))
        self.assertEqual(200, response.status_code)

        response = self.client.post(reverse('user:signup'), data={'username': 'unittest', 'password1': 'unittest'})
        self.assertEqual(200, response.status_code)
        form = response.context['form']
        self.assertTrue(form.is_bound)
        self.assertTrue(len(form.errors) > 0)

        # test normal signup.
        self.assertRaises(User.DoesNotExist, User.objects.get, username='unittest')
        response = self.client.post(reverse('user:signup'), data={'username': 'unittest', 'password1': 'unittest', 'password2': 'unittest', 'invitation_code': 'north', 'email': 'unittest@example.com'})
        self.assertRedirects(response, reverse('user:edit'))
        self.assertTrue(response.wsgi_request.user.is_authenticated())

        user = User.objects.get(username='unittest')
        self.assertEqual('unittest@example.com', user.email)

        user_profile = UserProfile(user)
        self.assertFalse(user_profile.has_profile())

        # test profile page, self.client is stateful, so post should be fine.
        post_data = {'first_name': 'Unit', 'last_name': 'Test', 'phone_main': '555-555-5555', 'email': user.email}
        response = self.client.post(reverse('user:edit'), post_data)
        self.assertTrue(response.status_code in (200, 302))
        user = User.objects.get(username='unittest')
        user_profile = UserProfile(user)
        self.assertTrue(user_profile.has_profile())
        self.assertEqual('555-555-5555', user_profile.profile.phone_main)

        # todo: update picture, change role, change centers.
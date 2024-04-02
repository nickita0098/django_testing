from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       author=cls.author,)
        cls.login_url = reverse('users:login')

        cls.urls_for_auth = (
            reverse('notes:list'),
            reverse('notes:add', args=None),
            reverse('notes:success'),
        )

        cls.urls_any = (
            reverse('notes:home'),
            cls.login_url,
            reverse('users:logout'),
            reverse('users:signup'),
        )

        cls.urls_for_author = (
            reverse('notes:edit', args=(cls.note.slug,)),
            reverse('notes:delete', args=(cls.note.slug,)),
            reverse('notes:detail', args=(cls.note.slug,)),
        )

    def setUp(self):
        self.author_client, self.reader_client = Client(), Client()
        self.author_client.force_login(self.author)
        self.reader_client.force_login(self.reader)

    def test_availability_for_author(self):
        """Все урлы доступны автору"""
        for url in self.urls_for_author + self.urls_for_auth + self.urls_any:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_not_author(self):
        """
        Все урлы, кроме редактирования, удаления
        и детали доступны не автору
        """
        for url in self.urls_for_author:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        for url in self.urls_for_auth + self.urls_any:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_not_anonim(self):
        """
        Все урлы кроме урлов аутонтефицированного пользователя
        и автора доступны анониму
        """
        for url in self.urls_any:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        for url in self.urls_for_author + self.urls_for_auth:
            with self.subTest(url=url):
                expected_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)

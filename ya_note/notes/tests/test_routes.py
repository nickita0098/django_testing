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

        cls.URL_NOTE_LIST = reverse('notes:list')
        cls.URL_NOTE_ADD = reverse('notes:add', args=None)
        cls.URL_NOTE_SUCCESS = reverse('notes:success')
        cls.URL_NOTE_HOME = reverse('notes:home')
        cls.URL_NOTE_LOGIN = reverse('users:login')
        cls.URL_NOTE_EDIT = reverse('notes:edit', args=(cls.note.slug,))
        cls.URL_NOTE_DELETE = reverse('notes:delete', args=(cls.note.slug,))
        cls.URL_NOTE_DETAIL = reverse('notes:detail', args=(cls.note.slug,))
        cls.URL_NOTE_LOGOUT = reverse('users:logout')
        cls.URL_NOTE_SIGNUP = reverse('users:signup')

        cls.ALL_URLS = (
            cls.URL_NOTE_LIST,
            cls.URL_NOTE_ADD,
            cls.URL_NOTE_SUCCESS,
            cls.URL_NOTE_HOME,
            cls.URL_NOTE_LOGIN,
            cls.URL_NOTE_EDIT,
            cls.URL_NOTE_DELETE,
            cls.URL_NOTE_DETAIL,
            cls.URL_NOTE_LOGOUT,
            cls.URL_NOTE_SIGNUP,
        )

    def setUp(self):
        self.author_client, self.reader_client = Client(), Client()
        self.author_client.force_login(self.author)
        self.reader_client.force_login(self.reader)

    def test_availability_for_author(self):
        """Все урлы доступны автору."""
        for url in self.ALL_URLS:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code,
                                 HTTPStatus.OK)

    def test_availability_for_not_author(self):
        """
        Все урлы, кроме редактирования, удаления
        и детали доступны не автору.
        """
        for url in self.ALL_URLS:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                if url in (self.URL_NOTE_EDIT,
                           self.URL_NOTE_DELETE,
                           self.URL_NOTE_DETAIL,):
                    self.assertEqual(response.status_code,
                                     HTTPStatus.NOT_FOUND)
                else:
                    self.assertEqual(response.status_code,
                                     HTTPStatus.OK)

    def test_availability_for_not_anonim(self):
        """
        Все урлы кроме урлов аутонтефицированного пользователя
        и автора доступны анониму.
        """
        for url in self.ALL_URLS:
            with self.subTest(url=url):
                expected_url = f'{self.URL_NOTE_LOGIN}?next={url}'
                response = self.client.get(url)
                if url in (self.URL_NOTE_HOME,
                           self.URL_NOTE_LOGIN,
                           self.URL_NOTE_LOGOUT,
                           self.URL_NOTE_SIGNUP,):
                    self.assertEqual(response.status_code,
                                     HTTPStatus.OK)
                else:
                    self.assertRedirects(response, expected_url)

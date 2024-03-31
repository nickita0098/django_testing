# news/tests/test_routes.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
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

    def test_pages_availability(self):
        """
        Главная страница доступна анонимному пользователю. Страницы
        регистрации пользователей, входа в учётную запись и выхода из
        неё доступны всем пользователям.
        """
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_comment_edit_and_delete(self):
        """
        Аутентифицированному пользователю доступна страница сосписком
        заметок notes/, страница успешного добавления заметки done/,
        страница добавления новой заметки add/.
        """
        self.client.force_login(self.author)
        for name in ('notes:list', 'notes:success', 'notes:add'):
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirects(self):
        """
        При попытке перейти на страницу списка заметок, страницу успешного
        добавления записи, страницу добавления заметки, отдельной заметки,
        редактирования или удаления заметки анонимный пользователь
        перенаправляется на страницу логина.
        """
        urls = (
            ('notes:detail', self.note.slug),
            ('notes:edit', self.note.slug),
            ('notes:delete', self.note.slug),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )
        login_url = reverse('users:login')
        for name, slug in urls:
            with self.subTest(name=name):
                if slug is not None:
                    url = reverse(name, args=(slug,))
                else:
                    url = reverse(name)
                expected_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)

    def test_pages_availability_for_different_users(self):
        """
        Страницы отдельной заметки, удаления и редактирования заметки
        доступны только автору заметки. Если на эти страницы попытается
        зайти другой пользователь — вернётся ошибка 404.
        """
        users_status = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        urls = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )
        for name in urls:
            for user, expected_status in users_status:
                self.client.force_login(user)
                with self.subTest(name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, expected_status)

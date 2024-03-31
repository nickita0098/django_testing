# news/tests/test_content.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       author=cls.author,)

    def test_notes_list_for_different_users(self):
        """
        Отдельная заметка передаётся на страницу со списком заметок в списке
        object_list в словаре context;
        В список заметок одного пользователя не попадают заметки
        другого пользователя.
        """
        users = (
            (self.author, True),
            (self.reader, False),
        )
        url = reverse('notes:list')

        for user, note_in_list_staus in users:
            self.client.force_login(user)
            response = self.client.get(url)
            object_list = response.context['object_list']
            note_in_list = self.note in object_list
            self.assertEqual(note_in_list, note_in_list_staus)

    def test_pages_contains_form(self):
        """На страницы создания и редактирования заметки передаются формы."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )

        for name, slug in urls:
            self.client.force_login(self.author)
            url = reverse(name, args=slug)
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)

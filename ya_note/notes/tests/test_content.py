# news/tests/test_content.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        note_title, note_text, note_author = 'Заголовок', 'Текст', cls.author
        cls.note = Note.objects.create(title=note_title,
                                       text=note_text,
                                       author=note_author,)
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add', args=None)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.user = None

    def setUp(self):
        self.author_client, self.reader_client = Client(), Client()
        self.author_client.force_login(self.author)
        self.reader_client.force_login(self.reader)

    def test_notes_list_for_author_user(self):
        """У заметка не появляется в списках заметок авторов"""
        response = self.author_client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), 1)
        note_in_list = self.note in object_list
        self.assertEqual(note_in_list, True)
        note_from_object_list = object_list.get(pk=1)
        self.assertEqual(note_from_object_list.title, self.note.title)
        self.assertEqual(note_from_object_list.text, self.note.text)
        self.assertEqual(note_from_object_list.author, self.note.author)

    def test_notes_list_for_reader_user(self):
        """У заметка не появляется в списках заметок не автора"""
        response = self.reader_client.get(self.list_url)
        object_list = response.context['object_list']
        note_in_list = self.note in object_list
        self.assertEqual(object_list.count(), 0)
        self.assertEqual(note_in_list, False)

    def test_pages_contains_form(self):
        """На страницы создания и редактирования заметки передаются формы."""
        urls = (
            (self.add_url),
            (self.edit_url),
        )
        for url in urls:
            response = self.author_client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)

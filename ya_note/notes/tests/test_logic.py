from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING


User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='автор')
        cls.not_author = User.objects.create(username='не автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.form_data = {'title': 'Новый заголовок',
                         'text': 'Новый текст',
                         'slug': 'new-slug'}
        cls.add_url = reverse('notes:add')
        cls.soccses_url = reverse('notes:success')

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку"""
        Note.objects.all().delete()
        node_count_old = Note.objects.count()
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.soccses_url)
        self.assertEqual(Note.objects.count(), node_count_old + 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Не залогиненный пользователь не может создать заметку."""
        Note.objects.all().delete()
        node_count_old = Note.objects.count()
        response = self.client.post(self.add_url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), node_count_old)

    def test_empty_slug(self):
        """
        Если при создании заметки не заполнен slug,
        то он формируется автоматически
        """
        Note.objects.all().delete()
        node_count_old = Note.objects.count()
        self.form_data.pop('slug')
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.soccses_url)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(Note.objects.count(), node_count_old + 1)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)


class TestCommentEditDelete(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='автор')
        cls.not_author = User.objects.create(username='не автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.form_data = {'title': 'Новый заголовок',
                         'text': 'Новый текст',
                         'slug': 'new-slug'}
        cls.note = Note.objects.create(title='Заголовок',
                                       text='Текст',
                                       author=cls.author)
        cls.add_url = reverse('notes:add')
        cls.soccses_url = reverse('notes:success')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        node_count_old = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertFormError(response,
                             form='form',
                             field='slug',
                             errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), node_count_old)

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свои заметки."""
        node_count_old = Note.objects.count()
        self.assertEqual(node_count_old, 1)
        response = self.author_client.post(self.edit_url, self.form_data)
        self.assertRedirects(response, self.soccses_url)
        self.note = Note.objects.get()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.author)

    def test_other_user_cant_edit_note(self):
        """Пользователь не может редактировать и удалять чужие заметки."""
        response = self.not_author_client.post(self.edit_url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get()
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, self.author)

    def test_author_can_delete_note(self):
        """Пользователь может удалять свои заметки."""
        node_count_old = Note.objects.count()
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), node_count_old - 1)

    def test_other_user_cant_delete_note(self):
        """Пользователь не может удалять чужие заметки."""
        node_count_old = Note.objects.count()
        response = self.not_author_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), node_count_old)

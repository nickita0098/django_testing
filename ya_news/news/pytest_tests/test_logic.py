from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, news, home_url):
    """Анонимный пользователь не может отправить комментарий."""
    comments_count_before = Comment.objects.count()
    client.post(home_url, data={'text': 'комментарий'})
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before


def test_user_can_create_comment(author, author_client, news, detail_url):
    """Авторизованный пользователь может отправить комментарий."""
    comments_count_before = Comment.objects.count()
    comment_text = 'комментарий'
    response = author_client.post(detail_url, data={'text': comment_text})
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before + 1
    comment = Comment.objects.get()
    assert comment.text == comment_text
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news, detail_url):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    comments_count_before = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before


def test_author_can_delete_comment(author_client, comment,
                                   delete_url, detail_url):
    """Авторизованный пользователь может удалять свои комментарии."""
    comments_count_before = Comment.objects.count()
    url_to_comments = f'{detail_url}#comments'
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before - 1


def test_user_cant_delete_comment_of_another_user(not_author_client,
                                                  delete_url):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comments_count_before = Comment.objects.count()
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before


def test_author_can_edit_comment(author_client, comment, edit_url, detail_url):
    """Авторизованный пользователь может редактировать свои комментарии."""
    comments_count_before = Comment.objects.count()
    data = {'text': 'комментарий'}
    response = author_client.post(edit_url, data=data)
    assertRedirects(response, f'{detail_url}#comments')
    edited_comment = Comment.objects.get()
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before
    assert edited_comment.text == data.get('text')
    assert edited_comment.news == comment.news
    assert edited_comment.author == comment.author
    assert edited_comment.created == comment.created


def test_user_cant_edit_comment_of_another_user(not_author_client,
                                                comment,
                                                edit_url):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    comments_count_before = Comment.objects.count()
    comment_text = 'комментарий'
    response = not_author_client.post(edit_url, data={'text': comment_text})
    assert response.status_code == HTTPStatus.NOT_FOUND
    edited_comment = Comment.objects.get()
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before
    assert edited_comment.text == comment.text
    assert edited_comment.news == comment.news
    assert edited_comment.author == comment.author
    assert edited_comment.created == comment.created

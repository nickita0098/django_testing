import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    """Анонимный пользователь не может отправить комментарий."""
    detail_url = reverse('news:detail', args=(news.pk,))
    client.post(detail_url, data={'text': 'комментарий'})
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(author, author_client, news):
    """Авторизованный пользователь может отправить комментарий."""
    comment_text = 'комментарий'
    detail_url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(detail_url, data={'text': comment_text})
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == comment_text
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, news):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    detail_url = reverse('news:detail', args=(news.pk,))
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, comment):
    """Авторизованный пользователь может удалять свои комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    news_url = reverse('news:detail', args=(comment.news.id,))
    url_to_comments = news_url + '#comments'
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client, comment):
    """Авторизованный пользователь может редактировать свои комментарии."""
    comment_text = 'комментарий'
    news_url = reverse('news:detail', args=(comment.news.id,))
    edit_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(edit_url, data={'text': comment_text})
    assertRedirects(response, news_url + '#comments')
    comment.refresh_from_db()
    assert comment.text == comment_text


def test_user_cant_edit_comment_of_another_user(not_author_client, comment):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    comment_text = 'комментарий'
    old_comment_text = comment.text
    edit_url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(edit_url, data={'text': comment_text})
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_comment_text

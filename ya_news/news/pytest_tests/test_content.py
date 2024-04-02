import pytest
from django.conf import settings

from news.forms import CommentForm


pytestmark = pytest.mark.django_db


def test_news_count(client, page_data, home_url):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, home_url):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert sorted_dates == all_dates


def test_comments_order(client, detail_url):
    """
    Комментарии на странице отдельной новости отсортированы в
    хронологическом порядке: старые в начале списка, новые — в конце.
    """
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, detail_url):
    """
    Анонимному пользователю недоступна форма для отправки комментария
    на странице отдельной новости.
    """
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(not_author_client, detail_url):
    """
    Авторизованному пользователю недоступна форма для отправки комментария
    на странице отдельной новости.
    """
    response = not_author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)

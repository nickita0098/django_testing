from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


HOME_URL = pytest.lazy_fixture('home_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')

ANONIM_CLIENT = pytest.lazy_fixture('anonim')
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')


@pytest.mark.parametrize(
    'url, client, status',
    (
        (HOME_URL, ANONIM_CLIENT, HTTPStatus.OK),
        (LOGIN_URL, ANONIM_CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, ANONIM_CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, ANONIM_CLIENT, HTTPStatus.OK),
        (DETAIL_URL, ANONIM_CLIENT, HTTPStatus.OK),
        (EDIT_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (DELETE_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
    )
)
def test_pages_availability_for_anonymous_user(url, client, status):
    """
    Главная страница доступна анонимному пользователю,
    страницы регистрации пользователей, входа в учётную
    запись и выхода из неё доступны анонимным пользователям,
    страница отдельной новости доступна анонимному пользователю,
    страницы удаления и редактирования комментария доступны автору,
    авторизованный пользователь не может зайти на страницы редактирования или
    удаления чужих комментариев (возвращается ошибка 404).
    """
    response = client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'url', (
        EDIT_URL,
        DELETE_URL,
    ),
)
def test_redirects(client, url):
    """
    При попытке перейти на страницу редактирования
    или удаления комментария анонимный пользователь
    перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)

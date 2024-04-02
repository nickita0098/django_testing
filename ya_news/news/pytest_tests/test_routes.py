from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, client, status',
    (
        (pytest.lazy_fixture('home_url'),
         pytest.lazy_fixture('anonim'),
         HTTPStatus.OK),
        (pytest.lazy_fixture('login_url'),
         pytest.lazy_fixture('anonim'),
         HTTPStatus.OK),
        (pytest.lazy_fixture('logout_url'),
         pytest.lazy_fixture('anonim'),
         HTTPStatus.OK),
        (pytest.lazy_fixture('signup_url'),
         pytest.lazy_fixture('anonim'),
         HTTPStatus.OK),
        (pytest.lazy_fixture('detail_url'),
         pytest.lazy_fixture('anonim'),
         HTTPStatus.OK),
        (pytest.lazy_fixture('edit_url'),
         pytest.lazy_fixture('not_author_client'),
         HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('delete_url'),
         pytest.lazy_fixture('not_author_client'),
         HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('edit_url'),
         pytest.lazy_fixture('author_client'),
         HTTPStatus.OK),
        (pytest.lazy_fixture('delete_url'),
         pytest.lazy_fixture('author_client'),
         HTTPStatus.OK),
    )
)
def test_pages_availability_for_anonymous_user(url, client, status):
    """
    Главная страница доступна анонимному пользователю.
    Страницы регистрации пользователей, входа в учётную
    запись и выхода из неё доступны анонимным пользователям.
    Страница отдельной новости доступна анонимному пользователю.
    Страницы удаления и редактирования комментария доступны автору.
    Авторизованный пользователь не может зайти на страницы редактирования или
    удаления чужих комментариев (возвращается ошибка 404).
    """
    response = client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'name', ('news:edit', 'news:delete'),
)
def test_redirects(client, name, comment):
    """
    При попытке перейти на страницу редактирования
    или удаления комментария анонимный пользователь
    перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.pk,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)

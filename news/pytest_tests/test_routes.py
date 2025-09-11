from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_fixture, client_fixture, status',
    (
        # Public pages for anonymous user (GET)
        ('home_url', 'client', HTTPStatus.OK),
        ('detail_url', 'client', HTTPStatus.OK),
        ('login_url', 'client', HTTPStatus.OK),
        ('signup_url', 'client', HTTPStatus.OK),
        # Comment pages access control (GET)
        ('comment_edit_url', 'author_client', HTTPStatus.OK),
        ('comment_delete_url', 'author_client', HTTPStatus.OK),
        ('comment_edit_url', 'not_author_client', HTTPStatus.NOT_FOUND),
        ('comment_delete_url', 'not_author_client', HTTPStatus.NOT_FOUND),
    ),
)
def test_get_statuses(request, url_fixture, client_fixture, status):
    url = request.getfixturevalue(url_fixture)
    client = request.getfixturevalue(client_fixture)
    response = client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'url_fixture',
    ('comment_delete_url', 'comment_edit_url'),
)
def test_anonymous_redirects_to_login_on_comment_pages(
    client, request, url_fixture, login_url,
):
    target_url = request.getfixturevalue(url_fixture)
    response = client.get(target_url)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, f'{login_url}?next={target_url}')


def test_post_logout_status(client, logout_url):
    response = client.post(logout_url)
    assert response.status_code == HTTPStatus.OK

from http import HTTPStatus
import pytest
from django.urls import reverse


@pytest.mark.parametrize(
    'url_name, needs_news',
    (
        ('news:home', False),
        ('news:detail', True),
    ),
)
@pytest.mark.django_db
def test_pages_availability_for_anonymous_user(client, url_name, needs_news):
    if needs_news:
        from news.models import News
        news = News.objects.create(title='Test title', text='Test text')
        url = reverse(url_name, kwargs={'pk': news.pk})
    else:
        url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('name', ('news:delete', 'news:edit'))
@pytest.mark.django_db
def test_comment_edit_delete_pages_available_for_author(author_client, comment, name):
    url = reverse(name, kwargs={'pk': comment.pk})
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('name', ('news:delete', 'news:edit'))
@pytest.mark.django_db
def test_anonymous_redirected_to_login_on_comment_pages(client, comment, name):
    login_url = reverse('users:login')
    target_url = reverse(name, kwargs={'pk': comment.pk})
    response = client.get(target_url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{login_url}?next={target_url}'


@pytest.mark.parametrize('name', ('news:delete', 'news:edit'))
@pytest.mark.django_db
def test_auth_user_cannot_access_others_comment_pages(not_author_client, comment, name):
    url = reverse(name, kwargs={'pk': comment.pk})
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND

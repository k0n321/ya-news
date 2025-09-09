from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertTemplateUsed

from django.urls import reverse

from news.forms import WARNING
from news.models import Comment

# Mark entire module as requiring the database
pytestmark = pytest.mark.django_db

def test_anonymous_cannot_post_comment(client, make_detail_url):
    detail_url = make_detail_url()
    comments_before = Comment.objects.count()
    response = client.post(
        detail_url,
        data={'text': 'Комментарий'},
        follow=True,
    )
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, 'registration/login.html')
    assert Comment.objects.count() == comments_before


def test_authorized_user_can_post_comment(
    author_client, author, news, make_detail_url,
):
    detail_url = make_detail_url()
    comments_before = Comment.objects.count()
    data = {'text': 'Новый комментарий'}
    response = author_client.post(detail_url, data=data)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, make_detail_url(anchor=True))
    assert Comment.objects.count() == comments_before + 1
    created = Comment.objects.get(news=news, author=author, text=data['text'])
    assert created.news == news
    assert created.author == author
    assert created.text == data['text']


def test_comment_with_bad_words_not_published(author_client, make_detail_url):
    detail_url = make_detail_url()
    comments_before = Comment.objects.count()
    data = {'text': 'Какой негодяй!'}
    response = author_client.post(detail_url, data=data)
    assert response.status_code == HTTPStatus.OK
    assertTemplateUsed(response, 'news/detail.html')
    form = response.context['form']
    assert form.is_bound
    assert 'text' in form.errors
    assert WARNING in form.errors['text']
    assert Comment.objects.count() == comments_before


def test_author_can_edit_own_comment(
    author_client, comment, make_detail_url,
):
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    new_text = 'Обновлённый текст'
    response = author_client.post(url, data={'text': new_text})
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, make_detail_url(anchor=True))
    comment.refresh_from_db()
    assert comment.text == new_text


def test_author_can_delete_own_comment(
    author_client, comment, make_detail_url,
):
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    comments_before = Comment.objects.count()
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, make_detail_url(anchor=True))
    assert Comment.objects.count() == comments_before - 1
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_auth_user_cannot_edit_others_comment(not_author_client, comment):
    url = reverse('news:edit', kwargs={'pk': comment.pk})
    old_text = comment.text
    response = not_author_client.post(
        url,
        data={'text': 'Хочу поменять чужой текст'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_text


def test_auth_user_cannot_delete_others_comment(not_author_client, comment):
    url = reverse('news:delete', kwargs={'pk': comment.pk})
    comments_before = Comment.objects.count()
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_before
    assert Comment.objects.filter(pk=comment.pk).exists()

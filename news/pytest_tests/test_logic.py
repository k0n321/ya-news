from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertTemplateUsed
from django.urls import reverse

from news.forms import WARNING, BAD_WORDS
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_cannot_post_comment(client, make_detail_url, login_url):
    detail_url = make_detail_url()
    comments_before = Comment.objects.count()
    response = client.post(
        detail_url,
        data={'text': 'Комментарий'},
    )
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, f'{login_url}?next={detail_url}')
    assert Comment.objects.count() == comments_before


def test_authorized_user_can_post_comment(
    author_client, author, news, make_detail_url,
):
    detail_url = make_detail_url()
    Comment.objects.all().delete()
    data = {'text': 'Новый комментарий'}
    response = author_client.post(detail_url, data=data)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, make_detail_url(anchor=True))
    assert Comment.objects.count() == 1
    created = Comment.objects.get()
    assert created.news == news
    assert created.author == author
    assert created.text == data['text']


def test_comment_with_bad_words_not_published(author_client, make_detail_url):
    detail_url = make_detail_url()
    comments_before = Comment.objects.count()
    data = {'text': f'Какой {BAD_WORDS[0]}!'}
    response = author_client.post(detail_url, data=data)
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == comments_before
    assertTemplateUsed(response, 'news/detail.html')
    form = response.context['form']
    assert form.is_bound
    assert 'text' in form.errors
    assert WARNING in form.errors['text']


def test_author_can_edit_own_comment(
    author_client, comment, comment_edit_url, make_detail_url,
):
    url = comment_edit_url
    new_text = 'Обновлённый текст'
    response = author_client.post(url, data={'text': new_text})
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, make_detail_url(anchor=True))
    updated = Comment.objects.get(pk=comment.pk)
    assert updated.text == new_text
    assert updated.author == comment.author
    assert updated.news == comment.news


def test_author_can_delete_own_comment(
    author_client, comment, comment_delete_url, make_detail_url,
):
    url = comment_delete_url
    comments_before = Comment.objects.count()
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assertRedirects(response, make_detail_url(anchor=True))
    assert Comment.objects.count() == comments_before - 1
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_auth_user_cannot_edit_others_comment(
    not_author_client, comment, comment_edit_url
):
    url = comment_edit_url
    response = not_author_client.post(
        url,
        data={'text': 'Хочу поменять чужой текст'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    updated = Comment.objects.get(pk=comment.pk)
    assert updated.text == comment.text
    assert updated.author == comment.author
    assert updated.news == comment.news


def test_auth_user_cannot_delete_others_comment(
    not_author_client, comment, comment_delete_url
):
    url = comment_delete_url
    comments_before = Comment.objects.count()
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_before
    assert Comment.objects.filter(pk=comment.pk).exists()

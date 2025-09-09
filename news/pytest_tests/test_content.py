from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.forms import CommentForm
from news.models import News

# Mark entire module as requiring the database
pytestmark = pytest.mark.django_db


def test_home_contains_no_more_than_ten_news(client, make_news_list, home_url):
    make_news_list(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_home_news_sorted_newest_first(client, make_news_list, home_url):
    make_news_list(12)
    response = client.get(home_url)
    object_list = response.context['object_list']
    dates = [item.date for item in object_list]
    assert dates == sorted(dates, reverse=True)


def test_detail_comments_sorted_oldest_first(client, author, news, make_detail_url):
    detail_url = make_detail_url()
    now = timezone.now()
    from news.models import Comment
    for i in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {i}',
        )
        comment.created = now + timedelta(minutes=i)
        comment.save()
    response = client.get(detail_url)
    assert 'news' in response.context
    news_obj = response.context['news']
    comments = list(news_obj.comment_set.all())
    timestamps = [c.created for c in comments]
    assert timestamps == sorted(timestamps)


def test_anonymous_has_no_comment_form(client, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert 'form' not in response.context


def test_authorized_has_comment_form(author_client, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)

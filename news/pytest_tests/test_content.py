import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_home_contains_no_more_than_ten_news(client, news_overflow, home_url):
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_home_news_sorted_newest_first(client, news_12, home_url):
    response = client.get(home_url)
    object_list = response.context['object_list']
    dates = [item.date for item in object_list]
    assert dates == sorted(dates, reverse=True)


def test_detail_comments_sorted_oldest_first(
    client, comments_ordered, detail_url
):
    response = client.get(detail_url)
    assert 'news' in response.context
    news_obj = response.context['news']
    comments = list(news_obj.comment_set.all())
    timestamps = [c.created for c in comments]
    assert timestamps == sorted(timestamps)


def test_anonymous_has_no_comment_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_has_comment_form(author_client, detail_url):
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)

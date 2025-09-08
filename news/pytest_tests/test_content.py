from datetime import datetime, timedelta

import pytest

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.forms import CommentForm
from news.models import News


@pytest.mark.django_db
def test_home_contains_no_more_than_ten_news(client):
    today = datetime.today()
    News.objects.bulk_create([
        News(
            title=f'Новость {i}',
            text='Текст',
            date=today - timedelta(days=i),
        )
        for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ])
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_home_news_sorted_newest_first(client):
    today = datetime.today()
    News.objects.bulk_create([
        News(
            title=f'Новость {i}',
            text='Текст',
            date=today - timedelta(days=i),
        )
        for i in range(12)
    ])
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    dates = [item.date for item in object_list]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_detail_comments_sorted_oldest_first(client, django_user_model):
    news = News.objects.create(title='Заголовок', text='Текст')
    author = django_user_model.objects.create(username='Комментатор')
    detail_url = reverse('news:detail', kwargs={'pk': news.pk})
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


@pytest.mark.django_db
def test_anonymous_has_no_comment_form(client):
    news = News.objects.create(title='Заголовок', text='Текст')
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_has_comment_form(author_client):
    news = News.objects.create(title='Заголовок', text='Текст')
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)

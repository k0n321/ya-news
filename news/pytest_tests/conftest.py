from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone
import pytest

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст новости')


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def signup_url():
    return reverse('users:signup')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', kwargs={'pk': news.pk})


@pytest.fixture
def comment_edit_url(comment):
    return reverse('news:edit', kwargs={'pk': comment.pk})


@pytest.fixture
def comment_delete_url(comment):
    return reverse('news:delete', kwargs={'pk': comment.pk})


@pytest.fixture
def news_overflow():
    start_date = datetime.today()
    count = settings.NEWS_COUNT_ON_HOME_PAGE + 1
    News.objects.bulk_create(
        (
            News(
                title=f'Новость {i}',
                text='Текст',
                date=start_date - timedelta(days=i),
            )
            for i in range(count)
        )
    )


@pytest.fixture
def detail_comments_url(detail_url):
    return detail_url + '#comments'


@pytest.fixture
def comments_ordered(author, news):
    now = timezone.now()
    for i in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {i}',
        )
        comment.created = now + timedelta(minutes=i)
        comment.save()

import pytest
from django.test.client import Client
from django.urls import reverse

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
def make_news_list():
    def _make(count: int, start_date=None, text: str = 'Текст'):
        from datetime import datetime, timedelta
        if start_date is None:
            start_date = datetime.today()
        News.objects.bulk_create(
            (
                News(
                    title=f'Новость {i}',
                    text=text,
                    date=start_date - timedelta(days=i),
                )
                for i in range(count)
            )
        )
    return _make


@pytest.fixture
def make_detail_url(news):
    def _make(anchor: bool = False) -> str:
        url = reverse('news:detail', kwargs={'pk': news.pk})
        return url + '#comments' if anchor else url
    return _make

# for each line split by ' for shop ' if exists pick index 1
# check db & mark availability, track_enabled = True
# has_products, checked = False
from os import environ
from django.core.wsgi import get_wsgi_application
from django.db import IntegrityError

environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopify_tracker_backend.settings')
application = get_wsgi_application()
from shops.models import Proxies


def main():
    urls_file = open('http.txt', 'r', encoding='utf-8')
    lines = [x.strip() for x in urls_file]
    for line in lines:
        proxy = line.split(',')
        try:
            proxy = Proxies.objects.create(schema='http', ip=proxy[0])
            print(f'{proxy} Inserted')
        except IntegrityError:
            print(f'http:{proxy[0]} Already exists')


if __name__ == '__main__':
    main()

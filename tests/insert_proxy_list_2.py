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
    urls_file = open('proxies.csv', 'r', encoding='utf-8')
    lines = [x.strip() for x in urls_file]
    for line in lines:
        proxy_list = line.split(',')
        print(proxy_list)
        print(proxy_list[0], ' ', proxy_list[1])
        # http,https
        # 1.0.205.87:8080,1.0.171.213:8080,1.0.136.16:4153,1.12.55.136:2080
        try:
            proxy = Proxies.objects.create(schema='http', ip=proxy_list[0])
            print(f'{proxy} Inserted')
        except IntegrityError:
            print(f'http:{proxy_list[0]} Already exists')
        try:
            proxy_2 = Proxies.objects.create(schema='https', ip=proxy_list[1])
            print(f'{proxy_2} Inserted')
        except IntegrityError:
            print(f'https://{proxy_list} Already exists')


if __name__ == '__main__':
    main()

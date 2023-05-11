# for each line split by ' for shop ' if exists pick index 1
# check db & mark availability, track_enabled = True
# has_products, checked = False
from os import environ
from django.core.wsgi import get_wsgi_application

environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopify_tracker_backend.settings')
application = get_wsgi_application()
from shops.models import Shops


def main():
    urls_file = open('cnx_erorr.txt', 'r', encoding='utf-8')
    lines = [x.strip() for x in urls_file]
    for line in lines:
        if ' for shop ' in line:
            site = line.split(' for shop ')[1]
            shop = Shops.objects.get(shop_url=site)
            shop.checked = False
            shop.track_enabled = True
            shop.save()


if __name__ == '__main__':
    main()

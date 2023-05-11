import os
import time

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopify_tracker_backend.settings')
application = get_wsgi_application()
from fp.fp import FreeProxy
from shops.models import Proxies
from django.db import IntegrityError
from Proxy_List_Scrapper import Scrapper, Proxy, ScrapperException


class ScrapProxies:
    @staticmethod
    def scrap():
        while True:
            google_proxy: str = FreeProxy(google=True).get()
            schema, ip = google_proxy.split('://')
            try:
                proxy = Proxies.objects.create(schema=schema, ip=ip)
                print(f'{proxy} Inserted')
            except IntegrityError:
                print(f'{google_proxy} Already exists')
            anonym_proxy: str = FreeProxy(anonym=True).get()
            schema, ip = anonym_proxy.split('://')
            try:
                proxy = Proxies.objects.create(schema=schema, ip=ip)
                print(f'{proxy} Inserted')
            except IntegrityError:
                print(f'{anonym_proxy} Already exists')
            elite_proxy: str = FreeProxy(elite=True).get()
            schema, ip = elite_proxy.split('://')
            try:
                proxy = Proxies.objects.create(schema=schema, ip=ip)
                print(f'{proxy} Inserted')
            except IntegrityError:
                print(f'{elite_proxy} Already exists')
            rand_proxy: str = FreeProxy(rand=True).get()
            schema, ip = rand_proxy.split('://')
            try:
                proxy = Proxies.objects.create(schema=schema, ip=ip)
                print(f'{proxy} Inserted')
            except IntegrityError:
                print(f'{rand_proxy} Already exists')

    @staticmethod
    def get_proxy_list():
        while True:
            time.sleep(2)
            proxy_list = FreeProxy().get_proxy_list(repeat=True)
            for proxy in proxy_list:
                try:
                    proxy = Proxies.objects.create(schema='http', ip=proxy)
                    print(f'{proxy} Inserted')
                except IntegrityError:
                    print(f'{proxy} Already exists')

    @staticmethod
    def new_proxies():
        while True:
            time.sleep(2)
            scrapper = Scrapper(category='ALL', print_err_trace=False)
            data = scrapper.getProxies()
            for item in data.proxies:
                try:
                    proxy = Proxies.objects.create(schema='http', ip='{}:{}'.format(item.ip, item.port))
                    print(f'{proxy} Inserted')
                except IntegrityError:
                    print(f'{item.ip, item.port} Already exists')


if __name__ == '__main__':
    proxies_scrapper = ScrapProxies()
    proxies_scrapper.scrap()

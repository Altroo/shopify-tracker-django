from typing import Union
from django.db.models import QuerySet
from shops.models import Shops, Proxies
from random import choice
import requests
from requests.exceptions import JSONDecodeError, ConnectionError
from fp.fp import FreeProxyException
from django.core.management.base import BaseCommand


class RemoveOutdatedShops:
    def __init__(self):
        self.shops: Union[list[Union[QuerySet, Shops]], None] = None
        self.products: dict = {}

    def start(self):
        self.shops: list[Union[QuerySet, Shops]] = list(
            Shops.objects.filter(track_enabled=True, checked=False).exclude(availability=False).order_by('id'))
        return self.load_products()

    def load_products(self) -> Union[list[Union[QuerySet, Shops]], None]:
        items = list(Proxies.objects.all())
        for shop in self.shops:
            # burned_proxies = []
            while True:
                try:
                    # proxy_str_: str = FreeProxy(rand=True, google=True,
                    #                             anonym=True, elite=True).get()
                    # schema_, ip_ = proxy_str_.split('://')
                    # proxy_ = {
                    #     schema_: ip_
                    # }
                    # if proxy_ in burned_proxies:
                    #     continue
                    random_proxy = choice(items)
                    proxy_ = {
                        random_proxy.schema: random_proxy.ip
                    }
                    print(f'Using proxy {proxy_} for shop {shop.shop_url}')
                    # sleep(randrange(1, 3))
                    # sleep(2)
                    try:
                        response = requests.get(self.product_info(shop.shop_url), proxies=proxy_)
                        if response.status_code == 404:
                            shop.availability = False
                            shop.track_enabled = False
                            shop.has_products = False
                            shop.checked = True
                            shop.save()
                            print(f"Link {shop.shop_url} returned 404, setting db tracked & availability to False.")
                            break
                        else:
                            try:
                                response = response.json()
                                try:
                                    error = response['errors'] if response['errors'] else None
                                    if error:
                                        shop.availability = False
                                        shop.track_enabled = False
                                        shop.has_products = False
                                        shop.checked = True
                                        shop.save()
                                        print(f"Link {shop.shop_url} returned Error, "
                                              f"setting db tracked & availability to False.")
                                        break
                                except KeyError:
                                    products = response['products'] if response['products'] else []
                                    if products.__len__() > 0:
                                        date = str(products[0]['updated_at'])
                                        # 2023-03-21T09:32:14-07:00
                                        if '2023-' in date:
                                            print(f'{shop.shop_url} Has updated products')
                                            shop.availability = True
                                            shop.track_enabled = True
                                            shop.has_products = True
                                            shop.checked = True
                                            shop.save()
                                            break
                                        else:
                                            print(f'{shop.shop_url} Has outdated products')
                                            shop.availability = False
                                            shop.track_enabled = False
                                            shop.checked = True
                                            shop.save()
                                            break
                                    else:
                                        print(f'{shop.shop_url} Has 0 products')
                                        shop.availability = False
                                        shop.track_enabled = False
                                        shop.has_products = False
                                        shop.checked = True
                                        shop.save()
                                        break
                            except JSONDecodeError:
                                print(f'Proxy 1 {proxy_} burned trying new proxy')
                                # burned_proxies.append(proxy_)
                                shop.availability = False
                                shop.track_enabled = False
                                shop.has_products = False
                                shop.checked = True
                                shop.save()
                                break
                    except ConnectionError:
                        print(f'Proxy 1 {proxy_} returned connectionError')
                        shop.availability = False
                        shop.track_enabled = False
                        shop.has_products = False
                        shop.checked = True
                        shop.save()
                        break
                except FreeProxyException:
                    print(f'There are no working proxies at this time. repeat')
                    continue
        return self.shops

    @staticmethod
    def product_info(shop_url: str) -> str:
        return f'{shop_url}/products.json'


class Command(BaseCommand):
    def handle(self, **options):
        # 120 shop / min
        # 7200 / hour
        # 172 800 / day
        outdated_removed = RemoveOutdatedShops()
        outdated_removed.start()

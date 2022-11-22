import json
import sys
from typing import Union

from django.core.management import BaseCommand
from django.db.models import QuerySet

from shops.models import Shops
# from products.models import Products
from csv import reader
from os import path
from collections import defaultdict
from time import sleep, mktime
from random import randrange
from django.db.utils import IntegrityError
import requests
import datetime


class ProductsTracker:
    parent_file_dir = path.abspath(path.join(path.dirname(__file__), "../../.."))

    @staticmethod
    def date_time_milliseconds(date_time_obj: datetime) -> int:
        return int(mktime(date_time_obj.timetuple()) * 1000)

    def __init__(self):
        self.shops: Union[list[Union[QuerySet, Shops]], None] = None
        # defaultdict(<class 'list'>, {0: [0], 1: [1], 2: [2], 3: [3], 4: [4]})
        self.products: defaultdict[list] = defaultdict(list)

    @staticmethod
    def product_info(shop_url: str) -> str:
        return f'{shop_url}/products.json'

    def track(self):
        self.shops: list[Union[QuerySet, Shops]] = list(
            Shops.objects.filter(track_enabled=True).exclude(availability=False))
        self.load_products()

    def load_products(self):
        for shop in self.shops:
            if shop.shop_url not in self.products.keys():
                # try:
                sleep(randrange(1, 10))
                response = requests.get(self.product_info(shop.shop_url)).json()
                started_at = self.date_time_milliseconds(datetime.datetime.utcnow())
                new_obj = {
                    'products': {},
                    'started_at': started_at,
                }
                print(new_obj)
                data = json.load(response)
                products = data['products'] if data['products'] else []
                print(data['products'])
                # for value in products:
                #     # new_obj['products'][value['id']] = self.create_product_object(value)
                #     new_obj['products'][value['id']]['sales'] = []
                #     self.products[shop.shop_url].append(new_obj)
                #     print(self.products)
                # sys.stdout.write(f"Added {shop.shop_url} with {len(self.products[shop.shop_url]['products'])} "
                #                 f"products to memory database.\n")
                # except Exception as e:
                #     sys.stdout.write(f'Exception fetching the json product : {e}.\n')

            else:
                print('in else')

    def remove_shop(self, index: int):
        shop_url: str = self.shops[index].shop_url
        del self.shops[index]
        sys.stdout.write(f'Removed ${shop_url} from memory database.\n')


class Command(BaseCommand):
    help = 'Products tracker'

    def handle(self, *args, **options):
        sys.stdout.write(f'Starting tracking Products.\n')
        self.start_in_memory_track()
        sys.stdout.write('\n')

    @staticmethod
    def start_in_memory_track():
        products_tracker = ProductsTracker()
        try:
            products_tracker.track()
            # products_tracker.remove_shop(0)
        except Exception as e:
            sys.stdout.write('{}.\n'.format(e))

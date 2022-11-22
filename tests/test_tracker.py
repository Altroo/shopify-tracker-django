import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopify_tracker_backend.settings')
application = get_wsgi_application()

import json
import sys
from typing import Union
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
        self.products: dict = {}

    @staticmethod
    def product_info(shop_url: str) -> str:
        return f'{shop_url}/products.json'

    def track(self):
        self.shops: list[Union[QuerySet, Shops]] = list(
            Shops.objects.filter(track_enabled=True).exclude(availability=False))
        self.load_products()

    def load_products(self):
        for shop in self.shops:
            # if shop.shop_url not in self.products.keys():
            sleep(randrange(1, 10))
            response = requests.get(self.product_info(shop.shop_url)).json()
            started_at = self.date_time_milliseconds(datetime.datetime.utcnow())
            products = response['products'] if response['products'] else []
            new_obj = {
                'products': {},
                'started_at': started_at,
            }
            for value in products:
                product_obj = self.create_product_object(value)
                new_obj['products'][product_obj['id']] = product_obj
            self.products[shop.shop_url] = new_obj
            print(f"Added {shop.shop_url} with {self.products[shop.shop_url]['products'].__len__()} "
                  f"products to memory database.\n")
            self.check_for_sales(shop.shop_url)

    @staticmethod
    def create_product_object(value: dict) -> dict:
        return {
            'id': value['id'],
            'title': value['title'],
            'vendor': value['vendor'],
            'handle': value['handle'],
            'published_at': value['published_at'],
            'created_at': value['created_at'],
            'updated_at': value['updated_at'],
            'variants': value['variants'],
            'images': value['images'],
            'options': value['options'],
            'tags': value['tags'],
            'product_type': value['product_type'],
            'body_html': value['body_html'],
            'sales': [],
        }

    def remove_shop(self, index: int):
        shop_url: str = self.shops[index].shop_url
        del self.shops[index]
        sys.stdout.write(f'Removed ${shop_url} from memory database.\n')

    def check_for_new_products(self, shop_url: str, data: dict):
        list_of_all_values = [value for elem in self.products[shop_url]['products'] for value in elem.values()]
        for product in data['products']:
            if not product['id'] in list_of_all_values:
                product_obj = self.create_product_object(product)
                self.products[shop_url]['products'][product_obj['id']] = product_obj
                print(f"Added new product ${product_obj['title']} from ${shop_url} to memory database.\n")
            break

    def get_latest_sale(self, shop_url: str, product_id: int) -> Union[str, None]:
        for key, value in self.products[shop_url]['products'].items():
            if key == product_id:
                return value.get('updated_at', None)

    def check_for_sales(self, shop_url: str):
        data: dict = requests.get(self.product_info(shop_url)).json()
        self.check_for_new_products(shop_url, data)
        for product_id, values in self.products[shop_url]['products'].items():
            last_sale: Union[str, None] = self.get_latest_sale(shop_url, product_id)
            # if (last_sale && product['updated_at'] !== last_sale) {
            if last_sale and values.get('updated_at') != last_sale:
                # const prod = app.shopify.database[shop_url]['products'][`${product['id']}`];
                prod = self.products[shop_url]['products'][product_id]


if __name__ == '__main__':
    products_tracker = ProductsTracker()
    products_tracker.track()

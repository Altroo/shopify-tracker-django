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
import jsondiff


class ProductsTracker:
    parent_file_dir = path.abspath(path.join(path.dirname(__file__), "../../.."))

    @staticmethod
    def date_time_milliseconds(date_time_obj: datetime) -> int:
        return int(mktime(date_time_obj.timetuple()) * 1000)

    def __init__(self):
        self.shops: Union[list[Union[QuerySet, Shops]], None] = None
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
        for product in data['products']:
            if not product['id'] in self.products[shop_url]['products'].keys():
                product_obj = self.create_product_object(product)
                self.products[shop_url]['products'][product_obj['id']] = product_obj
                print(f"Added new product ${product_obj['title']} from ${shop_url} to memory database.\n")
            else:
                print(f"Product ${product['title']} from ${shop_url} already exists in memory database.\n")

    def get_latest_sale(self, shop_url: str, product_id: int) -> Union[str, None]:
        for key, value in self.products[shop_url]['products'].items():
            if key == product_id:
                return value.get('updated_at', None)

    def check_for_diff(self, old_product: dict, new_product: dict):
        diff = jsondiff.diff(
            self.create_product_object(old_product),
            self.create_product_object(new_product)
        )
        sold_variant: Union[dict: None] = None
        new_sale: bool = False  # False ?

        if diff.items().__len__() <= 2:
            if diff['updated_at']:
                new_sale = True
                if diff['variants']:
                    for key, value in old_product['variants'].items:
                        if value['updated_at'] != new_product['variants'][key]['updated_at']:
                            sold_variant = new_product['variants'][key]
                            break

        return {
            'diff': diff,
            'new_sale': new_sale,
            # 'sold_variant': sold_variant if sold_variant is not None else None
            'sold_variant': sold_variant
        }

    def update_latest_sale(self, shop_url: str, data: dict, sold_variant: Union[dict, None]):
        self.products[shop_url]['products'][data['id']]['sales'].append({
            'time': data['updated_at'],
            'variant': sold_variant,
            'price': sold_variant['price'] if sold_variant is not None else data['variants'][0]['price'],
        })
        self.products[shop_url]['products'][data['id']]['updated_at'] = data['updated_at']

    @staticmethod
    def find_image_by_id(images: dict, id_: str):
        image_url = None
        for image in images:
            if image['id'] == id_:
                image_url = image['src']
                break
        return image_url

    def get_product_sales_amount(self, shop_url: str, product_id: str, variant_id=None) -> dict:
        variant_sales = 0.0
        variant_sales_array = []
        product_sales = 0.0
        sale: dict
        for sale in self.products[shop_url]['products'][product_id]['sales']:
            if variant_id:
                if sale['variant']['product_id'] == variant_id:
                    variant_sales_array.append(sale)
                    variant_sales += float(sale['price'])
                product_sales += float(sale['price'])
        return {
            'variant': variant_sales,
            'variant_quantity': variant_sales_array.__len__(),
            'product': product_sales,
            'product_quantity': self.products[shop_url]['products'][product_id]['sales'].__len__(),
        }

    def get_shop_sales_amount(self, shop_url: str) -> Union[float, int]:
        summary = 0
        for key, value in self.products[shop_url]['products'].items():
            product_sales = self.get_product_sales_amount(shop_url, value['id'])
            summary += float(product_sales['product'])
        return summary

    def on_new_sale(self, shop_url: str, product: dict, sold_variant: [dict, None]):
        pass

    def check_for_sales(self, shop_url: str):
        data: dict = requests.get(self.product_info(shop_url)).json()
        self.check_for_new_products(shop_url, data)

        product: dict
        for product in data['products']:
            last_sale: Union[str, None] = self.get_latest_sale(shop_url, product['id'])
            # unecessary to add same variable on both check sides but i'm just translating lol
            if last_sale and product['updated_at'] != last_sale:
                prod: dict = self.products[shop_url]['products'][product['id']]
                diff = jsondiff.diff(
                    self.create_product_object(product),
                    self.create_product_object(prod)
                )
                if diff.items().__len__() <= 2 and diff['updated_at']:
                    sold_variant: Union[dict, None] = None
                    if diff['variants']:
                        check: dict = self.check_for_diff(prod, product)
                        sold_variant = check['sold_variant']
                    self.update_latest_sale(shop_url, product, sold_variant)
                    print(f"{shop_url} {self.products[shop_url]['products'][product['id']]['sales'].__len__()} "
                          f"New sale -> {product['title']}")

                    self.on_new_sale(shop_url, product, sold_variant)


if __name__ == '__main__':
    products_tracker = ProductsTracker()
    products_tracker.track()

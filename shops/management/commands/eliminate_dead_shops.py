from typing import Union
from django.db.models import QuerySet
from shops.models import Shops, Configs
from products.models import Products
from os import path
from time import mktime, sleep
from threading import Thread
# from random import randrange
import requests
from requests.exceptions import RequestException
import datetime
import jsondiff
# import sys
# from proxy_list import ProxyList
from fp.fp import FreeProxy, FreeProxyException
from django.core.management import BaseCommand
from django.core.paginator import Paginator


class Styles:
    colors = [
        '\033[1;30m', '\033[1;31m', '\033[1;32m', '\033[1;33m', '\033[1;34m',
        '\033[1;35m', '\033[1;36m', '\033[1;37m', '\033[90m', '\033[92m',
        '\033[1;41m', '\033[1;42m', '\033[1;43m', '\033[1;44m', '\033[1;45m',
        '\033[1;46m', '\033[1;47m', '\033[0;30;47m', '\033[0;31;47m', '\033[0;32;47m',
        '\033[0;33;47m', '\033[0;34;47m', '\033[0;35;47m', '\033[0;36;47m',
        '\033[1;30m', '\033[1;31m', '\033[1;32m', '\033[1;33m', '\033[1;34m',
        '\033[1;35m', '\033[1;36m', '\033[1;37m', '\033[90m', '\033[92m',
    ]


class ProductsTracker(Thread):
    parent_file_dir = path.abspath(path.join(path.dirname(__file__), "../../.."))

    @staticmethod
    def date_time_milliseconds(date_time_obj: datetime) -> float:
        return float(mktime(date_time_obj.timetuple()) * 1000)

    def __init__(self, color, threads, paginated):
        Thread.__init__(self)
        self.threads = threads
        self.color = color
        self.paginated = paginated
        self.shops: Union[list[Union[QuerySet, Shops]], None] = None
        self.db_shop: Union[QuerySet, Shops, None] = None
        # self.shops: Union[list[Union[QuerySet, Shops]], None] = None
        self.products: dict = {}

    @staticmethod
    def product_info(shop_url: str) -> str:
        return f'{shop_url}/products.json'

    def run(self):
        while self.paginated.page(int(self.color + 1)).has_next():
            ids_list = []
            for id_ in self.paginated.page(int(self.color + 1)).object_list:
                ids_list.append(id_.pk)
            self.shops = Shops.objects.filter(id__in=ids_list, checked=False).order_by('-id')
            # self.shops: list[Union[QuerySet, Shops]] = list(
            #     Shops.objects.filter(track_enabled=True, has_products=False).exclude(availability=False))
            self.load_products()

    def print_style(self, message):
        print(Styles.colors[self.color] + message, '\033[0m')

    def load_products(self) -> Union[list[Union[QuerySet, Shops]], None]:
        for shop in self.shops:
            # sleep(randrange(1, 10))
            # proxies = ProxyList()
            proxy_str: str = FreeProxy(rand=True).get()
            schema, ip = proxy_str.split('://')
            proxy = {
                schema: ip
            }
            try:
                # self.print_style(f"Checking {shop.shop_url.replace('https://', '')}")
                try:
                    response = requests.get(self.product_info(shop.shop_url), proxies=proxy)
                    response = response.json()
                    started_at = self.date_time_milliseconds(datetime.datetime.utcnow())
                    try:
                        products = response['products'] if response['products'] else []
                        new_obj = {
                            'products': {},
                            'started_at': started_at,
                        }
                        for value in products:
                            product_obj = self.create_product_object(value)
                            new_obj['products'][product_obj['id']] = product_obj
                            del product_obj['sales']
                            try:
                                Products.objects.update_or_create(shop=shop, product=product_obj)
                            except Products.MultipleObjectsReturned:
                                pass
                        self.products[shop.shop_url] = new_obj
                        self.print_style(f"Added {shop.shop_url.replace('https://', '')} with "
                                         f"{self.products[shop.shop_url]['products'].__len__()} "
                                         f"products to memory database.")
                        if self.products[shop.shop_url]['products'].__len__() > 0:
                            shop.has_products = True
                            shop.checked = True
                            shop.save()
                        else:
                            shop.availability = False
                            shop.track_enabled = False
                            shop.has_products = False
                            shop.checked = True
                            shop.save()
                    except (KeyError, TypeError):
                        self.print_style(f"Link {shop.shop_url.replace('https://', '')} Didn't complete setup")
                        shop.availability = False
                        shop.track_enabled = False
                        shop.has_products = False
                        shop.checked = True
                        shop.save()
                except RequestException as e:
                    self.print_style(f"Link {shop.shop_url.replace('https://', '')} returned {e.strerror}")
                    shop.availability = False
                    shop.track_enabled = False
                    shop.has_products = False
                    shop.checked = True
                    shop.save()
            except FreeProxyException as e:
                self.print_style(f"Link {shop.shop_url.replace('https://', '')} returned {e.message}")
        return self.shops

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
        self.print_style(f'Removed {shop_url} from memory database.')
        # sys.stdout.write(f'Removed {shop_url} from memory database.\n')

    def check_for_new_products(self, shop_url: str, data: dict):
        for product in data['products']:
            if not product['id'] in self.products[shop_url]['products'].keys():
                product_obj = self.create_product_object(product)
                self.products[shop_url]['products'][product_obj['id']] = product_obj
                self.print_style(f"Added new product {product_obj['title']} from {shop_url} to memory database.")
                del product_obj['sales']
                shop = Shops.objects.get(shop_url=shop_url)
                Products.objects.update_or_create(shop=shop, product=product_obj)

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
        new_sale: bool = False

        if diff.items().__len__() <= 2:
            if diff['updated_at']:
                new_sale = True
                if diff['variants']:
                    for key, variant in enumerate(old_product['variants']):
                        for item in variant.items():
                            if item[0] == 'updated_at' and item[1] != new_product['variants'][key]['updated_at']:
                                sold_variant = new_product['variants'][key]
                                break

        return {
            'diff': diff,
            'new_sale': new_sale,
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
            if variant_id and sale['variant'] is not None and 'product_id' in sale['variant'].keys():
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

    def on_new_sale(self, shop_url: str, data: dict, sold_variant: [dict, None]):
        field_text = ''
        all_together = self.get_product_sales_amount(
            shop_url,
            data['id'],
            sold_variant['product_id'] if sold_variant else None
        )
        if sold_variant:
            for key in ['title', 'sku', 'compare_at_price', 'price']:
                if sold_variant[key]:
                    field_text += f'{key}: {sold_variant[key]} \n '

        summary_shop = self.get_shop_sales_amount(shop_url)

        field = {
            'name': 'Variante:',
            'value': field_text,
        } if sold_variant else None

        field_2 = {
            'name': 'Statistics (Variante):',
            'value': f"Estimated earnings: {all_together['variant']} \n "
                     f"Quantity sold: {all_together['variant_quantity']}x \n "
        } if sold_variant else None

        field_3 = {
            'name': 'Statistics (Shop):',
            'value': f"Estimated earnings: {summary_shop} \n "
        }

        price = data['variants'][0]['price']
        if data['variants'][0]['compare_at_price']:
            price = f"{data['variants'][0]['price']} ~~{data['variants'][0]['compare_at_price']}~~"

        url = data['images'][0]['src']
        if sold_variant and sold_variant['featured_image']:
            url = self.find_image_by_id(data['images'], sold_variant['featured_image']['id'])

        embed = {
            'info': {
                'title': f"New sale: {shop_url}",
                'description':
                    f"Click here to go to the product page : {shop_url}/products/{data['handle']} \n "
                    f"Product : {data['title']} \n "
                    f"Sold at : {self.get_readable_date(data['updated_at'])} \n "
                    f"Tracker started at : {self.get_date_string_serv(self.products[shop_url]['started_at'])} \n "
                    f"Price : {price} \n ",
            },
            'thumbnail': {
                'url': url
            },
            'fields': [
                field,
                {
                    'name': 'Statistics (product): ',
                    'value': f"Earnings: {all_together['product']} \n "
                             f"Sold : {all_together['product_quantity']}x \n "
                },
                field_2,
                field_3
            ] if sold_variant else [
                {
                    'name': 'Statistics (product): ',
                    'value': f"Earnings: {all_together['product']} \n "
                             f"Sold : {all_together['product_quantity']}x \n "
                },
                field_3
            ]
        }
        # /** ** sys.stdout.writes the result that is sent to discord ** **/
        self.print_style(str(embed))

    @staticmethod
    def get_date_string_serv(timestamp: float) -> str:
        return f"{str(datetime.datetime.fromtimestamp(timestamp / 1000))}"

    @staticmethod
    def get_readable_date(date: str) -> str:
        return f"{str(datetime.datetime.strptime(date[0:-6], '%Y-%m-%dT%H:%M:%S'))}"

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
                    if 'variants' in diff.keys():
                        check: dict = self.check_for_diff(prod, product)
                        sold_variant = check['sold_variant']
                    self.update_latest_sale(shop_url, product, sold_variant)
                    self.print_style(f"{shop_url} - just sold : "
                                     f"{self.products[shop_url]['products'][product['id']]['sales'].__len__()} \n"
                                     f"New sale -> {product['title']}")
                    self.on_new_sale(shop_url, product, sold_variant)


def template(text):
    return """
 __________________________
< {} >
 --------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\\
                ||----w | \\
                ||     ||
""".format(text)


class Command(BaseCommand):
    help = 'Tracking Products'

    def handle(self, *args, **options):
        print('Start Tracking Available & tracked shops.\n')
        self.track()
        print('\n')

    @staticmethod
    def track():
        threads = 0
        while True:
            try:
                threads = int(input(template("How Many Threads To use ? type here 30: ")))
            except ValueError:
                print(template("Sorry, I didn't understand that."))
                continue
            else:
                break
        shops = Shops.objects.filter(track_enabled=True, has_products=False, checked=False) \
            .exclude(availability=False).order_by('-id')
        paginated = Paginator(shops, threads)
        bots = [ProductsTracker(x, threads, paginated) for x in range(0, threads)]
        for bot in bots:
            bot.start()
            sleep(2)
        # waiting all bots to finish before start tracking
        for bot in bots:
            bot.join()
        # products_tracker = ProductsTracker()
        # Filter shops by has products
        # shops = products_tracker.track()

        # # Start tracking
        # def set_interval(func, sec, shop_url):
        #     def func_wrapper():
        #         set_interval(func, sec, shop_url)
        #         func(shop_url)
        #
        #     t = Timer(sec, func_wrapper)
        #     t.start()
        #     return t
        #
        # interval = Configs.objects.all().first().interval
        # for shop_ in shops:
        #     if shop_.has_products:
        #         set_interval(products_tracker.check_for_sales, interval, shop_.shop_url)

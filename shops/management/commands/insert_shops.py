import sys
from django.core.management import BaseCommand
from shops.models import Shops
from csv import reader
from os import path
from django.db.utils import IntegrityError
import requests
from requests.exceptions import SSLError, ConnectionError


class InsertShops:
    parent_file_dir = path.abspath(path.join(path.dirname(__file__), "../../.."))

    def insert(self):
        with open(self.parent_file_dir + '/csv_data/shops_list.csv', 'r+', encoding='UTF8') as f:
            csv_reader = reader(f)
            for row in csv_reader:
                url = 'https://' + row[0]
                status = False
                try:
                    response = requests.get(url)
                    status = response.ok
                except (SSLError, ConnectionError):
                    print("Skipped due to SSLError, most likely the shop didn't finish setting up the "
                          "new web address, or 404")
                try:
                    Shops.objects.create(shop_url=url, availability=status)
                except IntegrityError:
                    print('Skipping shop url already exists.')


class Command(BaseCommand):
    help = 'Insert Shops'

    def handle(self, *args, **options):
        sys.stdout.write(f'Start processing Shops.\n')
        self.insert()
        sys.stdout.write('\n')

    @staticmethod
    def insert():
        insert_shops = InsertShops()
        try:
            insert_shops.insert()
        except Exception as e:
            sys.stdout.write('{}.\n'.format(e))

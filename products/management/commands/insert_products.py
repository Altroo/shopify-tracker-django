# import sys
# from django.core.management import BaseCommand
# # from shops.models import Shops
# from csv import reader
# from os import path
# from django.db.utils import IntegrityError
#
#
# class InsertShops:
#     parent_file_dir = path.abspath(path.join(path.dirname(__file__), "../../.."))
#
#     def insert(self):
#         with open(self.parent_file_dir + '/csv_data/categories.csv', 'r+', encoding='UTF8') as f:
#             csv_reader = reader(f, delimiter=',')
#             for row in csv_reader:
#                 try:
#                     pass
#                     # Shops.objects.create(name=row[0])
#                 except IntegrityError:
#                     continue
#
#
# class Command(BaseCommand):
#     help = 'Insert Shops'
#
#     def handle(self, *args, **options):
#         sys.stdout.write(f'Start processing Shops.\n')
#         self.insert()
#         sys.stdout.write('\n')
#
#     @staticmethod
#     def insert():
#         insert_shops = InsertShops()
#         try:
#             insert_shops.insert()
#         except Exception as e:
#             sys.stdout.write('{}.\n'.format(e))

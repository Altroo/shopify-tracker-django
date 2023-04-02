import os
import django
from django.db import IntegrityError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopify_tracker_backend.settings')
django.setup()

from time import sleep
import requests
from shops.models import Shops, Configs
from bs4 import BeautifulSoup
from mmap import mmap
from os import path, listdir, remove, makedirs
from threading import Thread
from shutil import move
from datetime import datetime
import re
import atexit
import sys

current_file_dir = path.dirname(path.abspath(__file__))


class Styles:
    colors = [
        '\033[1;30m', '\033[1;31m', '\033[1;32m', '\033[1;33m', '\033[1;34m',
        '\033[1;35m', '\033[1;36m', '\033[1;37m', '\033[90m', '\033[92m',
        '\033[1;41m', '\033[1;42m', '\033[1;43m', '\033[1;44m', '\033[1;45m',
        '\033[1;46m', '\033[1;47m', '\033[0;30;47m', '\033[0;31;47m', '\033[0;32;47m',
        '\033[0;33;47m', '\033[0;34;47m', '\033[0;35;47m', '\033[0;36;47m'
    ]


class Scrapify(Thread):
    def __init__(self, color, threads, last_date):
        Thread.__init__(self)
        self.threads = threads
        self.color = color
        self.last_date = last_date

    def run(self):
        files_input = self.setup()
        if files_input is None:
            return None
        else:
            return True

    def setup(self):
        input_file = self.get_input_file()
        if input_file is not None:
            self.get_data(input_file)
            return True
        else:
            return None

    @staticmethod
    def sorted_alphanumeric(folder):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(folder, key=alphanum_key)

    def get_input_file(self):
        try:
            file = self.sorted_alphanumeric(listdir(current_file_dir + '/data/input/'))[0]
        except IndexError:
            return None
        inputs = file if file.startswith('file_') else None
        if inputs is None:
            return None
        else:
            path_ = current_file_dir + '/data/temp/' + inputs
            try:
                move(current_file_dir + '/data/input/' + inputs, path_)
            except FileNotFoundError:
                print(Styles.colors[self.color] + 'get_input_file() FileNotFoundError ' + str(inputs) +
                      ' file taken by another Thread', '\033[0m')
                self.getting_another_file()
            else:
                return path_

    def getting_another_file(self):
        input_file = self.get_input_file()
        if input_file is not None:
            self.get_data(input_file)
        else:
            return True

    def get_data(self, input_file):
        my_switch = False
        try:
            print(Styles.colors[self.color] + '=' * 87, '\033[0m')
            print(Styles.colors[self.color] + ' input_file : ' + input_file, '\033[0m')

            print(Styles.colors[self.color] + '=' * 87, '\033[0m')
            urls_file = open(input_file, 'r', encoding='utf-8')
            urls = [x.strip() for x in urls_file]
            # last_date = get_last_used_date()  # example 2022-11-03
            for url in urls:
                print(Styles.colors[self.color] + ' url : ' + url, '\033[0m')
                sleep(2)
                html = requests.get(url)
                soup = BeautifulSoup(html.content, 'html.parser')
                # results = soup.find_all('span', attrs={'class': 'typeText'})
                results = soup.find_all('div', attrs={'class': 'blogContent'})
                # if current thread date > last used date : then we write the new date - else we skip
                current_thread_date = url.split('https://www.merchantgenius.io/shop/date/')[1]  # example : 2022-11-02
                for result in results:
                    shop_link = result.find_all('span', attrs={'class': 'typeText'})[0].text
                    try:
                        currency_country = result.select('img + span')[0].text.rstrip() \
                            .replace('(', '').replace(')', '').split('/')
                        currency = currency_country[0].rstrip()
                        country = currency_country[1].lstrip()
                    except IndexError:
                        currency_country = result.select('img + span')[1].text.rstrip() \
                            .replace('(', '').replace(')', '').split('/')
                        currency = currency_country[0].rstrip()
                        country = currency_country[1].lstrip()
                    print(Styles.colors[self.color] + 'Found url : {} - currrency : {} - country : {} - date : {}'
                          .format(shop_link, currency, country, current_thread_date), '\033[0m')
                    self.write_result(shop_link, currency, country, current_thread_date)
                if not self.last_date:
                    last_date_file = open(current_file_dir + '/data/last_used_date_{}.txt'.format(self.color), 'w',
                                          encoding='utf-8')
                    last_date_file.write(current_thread_date)
                    print(Styles.colors[self.color] + 'writing date : ', current_thread_date, '\033[0m')
                    last_date_file.flush()
                    last_date_file.close()
                else:
                    if datetime.strptime(self.last_date, '%Y-%m-%d') < datetime.strptime(current_thread_date,
                                                                                         '%Y-%m-%d'):
                        last_date_file = open(current_file_dir + '/data/last_used_date_{}.txt'.format(self.color), 'w',
                                              encoding='utf-8')
                        last_date_file.write(current_thread_date)
                        last_date_file.flush()
                        last_date_file.close()
            urls_file.close()
        except IOError as e:
            print(Styles.colors[self.color] + 'Could not read file: ', input_file, ' {}'.format(e.strerror), '\033[0m')
            my_switch = True
        finally:
            my_file = path.basename(input_file)
            # print(Styles.colors[self.color] + 'End of the object using file : {}'.format(my_file), '\033[0m')
            if my_switch is not True:
                self.delete_input_file(input_file)
                close = self.getting_another_file()
                if close is True:
                    self.end_script()
            else:
                self.copy_back_temp_file(input_file, my_file)
                self.end_script()

    def write_result(self, tableau, currency, country, current_thread_date):
        last_input_file = self.get_available_output_files()
        # print(Styles.colors[self.color] + 'Calling get_line_number()', '\033[0m')
        line_number = self.get_line_number(last_input_file)
        if line_number >= 50 or last_input_file == 0:
            # print(Styles.colors[self.color] + 'Calling write() with >= 50 or == 0', '\033[0m')
            self.write(tableau, currency, country, current_thread_date, last_input_file, False)
        else:
            # print(Styles.colors[self.color] + 'Calling write()', '\033[0m')
            self.write(tableau, currency, country, current_thread_date, last_input_file, True)

    def get_line_number(self, number):
        # print(Styles.colors[self.color] + 'get_line_number() called', '\033[0m')
        lines = 0
        try:
            f = open(current_file_dir + '/data/output/file_' + str(number) + '.txt', 'r+', encoding='utf-8')
            try:
                buf = mmap(f.fileno(), 0)
                readline = buf.readline
                while readline():
                    lines += 1
                f.close()
            except ValueError as err:
                print(Styles.colors[self.color] + 'nmap get_line_number() {}'.format(err), '\033[0m')
        except FileNotFoundError as err:
            if number > 0:
                print(Styles.colors[self.color] + 'get_line_number() FileNotFoundError {}'.format(err), '\033[0m')
        return lines

    def write(self, tableau, currency, country, current_thread_date, last_input_file, switch):
        # print(Styles.colors[self.color] + 'write() called', '\033[0m')
        my_path = '/data/output/file_'
        if switch is False:
            input_results = current_file_dir + my_path + str(int(last_input_file + 1)) + '.txt'
            # print(Styles.colors[self.color] + 'write() switch is False', '\033[0m')
        else:
            input_results = current_file_dir + my_path + str(last_input_file) + '.txt'
            # print(Styles.colors[self.color] + 'write() switch is True', '\033[0m')
        try:
            # print(Styles.colors[self.color] + 'Calling basic_append()', '\033[0m')
            self.basic_append(input_results, tableau, currency, country, current_thread_date)
        except IOError:
            print(Styles.colors[self.color] + 'Could not write to the file : ', input_results, '\033[0m')

    def delete_input_file(self, input_file):
        try:
            remove(input_file)
        except OSError as e:
            print(Styles.colors[self.color] + 'Could not remove file : ', input_file,
                  ' {}'.format(e.strerror), '\033[0m')

    def copy_back_temp_file(self, input_file, my_file):
        try:
            # print(Styles.colors[self.color] + 'Moving back {} to data/input'.format(my_file), '\033[0m')
            move(input_file, current_file_dir + '/data/input/')
        except FileNotFoundError as e:
            print(Styles.colors[self.color] + 'ERROR copy_back_temp_file : {} {}'.format(e.strerror, my_file),
                  '\033[0m')

    def end_script(self):
        print(Styles.colors[self.color] + 'Ending script', '\033[0m')

    @staticmethod
    def basic_append(file_name, value, currency, country, current_thread_date):
        # print(Styles.colors[self.color] + 'basic_append called()', '\033[0m')
        if value != '':
            url = 'https://' + value
            try:
                Shops.objects.create(shop_url=url, currency=currency, country=country,
                                     availability=False, track_enabled=False, site_date=current_thread_date)
            except IntegrityError:
                print('Already exists')
            # myfile = open(file_name, 'a+', encoding='utf-8')
            # myfile.write(str(value) + ',' + str(currency) + ',' + str(country) + ',' + str(current_thread_date) + '\n')
            # # myfile.flush()
            # myfile.close()

    @staticmethod
    def get_available_output_files():
        # print(Styles.colors[self.color] + 'get_available_output_files() called', '\033[0m')
        inputs = [file for file in listdir(current_file_dir + '/data/output/') if file.startswith('file_')]
        return int(len(inputs))


def read_input_files():
    inputs = [file for file in listdir(current_file_dir + '/data/input/') if file.startswith('file_')]
    return int(len(inputs))


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


def dividing_file(root_file, counter):
    lines_per_file = 50
    inputfiles = None
    input_folder = current_file_dir + '/data/input/'
    bigfile = open(root_file, encoding='utf-8')
    for lineno, line in enumerate(bigfile):
        if lineno % lines_per_file == 0:
            if inputfiles:
                inputfiles.close()
            counter += 1
            inputfiles = open(input_folder + 'file_{}.txt'.format(str(counter)), "a+")
        inputfiles.write(line)
    if inputfiles:
        inputfiles.close()
    bigfile.close()


def get_last_used_date():
    return Configs.objects.get(pk=1).last_used_date
    # last_used_date_file = current_file_dir + '/data/last_used_date.txt'
    # if not path.exists(last_used_date_file):
    #     return None
    # else:
    #     last_date_file = open(last_used_date_file, 'r', encoding='utf-8')
    #     if last_date_file.readable():
    #         last_date = [x.strip() for x in last_date_file]
    #         last_used_date = last_date[0]
    #         last_date_file.close()
    #         return last_used_date
    #     return None


def get_initial_data():
    # Read last used date file then generate new links if file not exist then start from scratch
    last_date = get_last_used_date()
    file_name = current_file_dir + '/data/all_dates.txt'
    url = 'https://www.merchantgenius.io'
    root_response = requests.get(url)
    root_soop = BeautifulSoup(root_response.content, 'html.parser')
    root_results = root_soop.find_all('button', attrs={'class': 'dateLinks'})
    # in short this assures the all_dates.txt file
    # to be sorted from the lowest date to the highest
    if last_date is not None:
        previous_lines_file = open(file_name, 'r+', encoding='utf-8')
        previous_urls_list = [*previous_lines_file.readlines()]
        previous_lines_file.close()
        open(file_name, 'w').close()
        myfile = open(file_name, 'a+', encoding='utf-8')
        urls_list = []
        for result in root_results:
            sub_link = result.parent.attrs.get('href')
            sub_link_date = sub_link.split('/shop/date/')[1]
            if datetime.strptime(last_date, '%Y-%m-%d') < datetime.strptime(sub_link_date, '%Y-%m-%d'):
                urls_list.append(str('{}{}\n'.format(url, sub_link)))
            else:
                continue
        myfile.writelines(previous_urls_list)
        myfile.writelines(sorted(urls_list))
        myfile.flush()
    else:
        # empty file if exists then append
        open(file_name, 'w').close()
        myfile = open(file_name, 'a+', encoding='utf-8')
        urls_list = []
        for result in root_results:
            sub_link = result.parent.attrs.get('href')
            urls_list.append(str('{}{}\n'.format(url, sub_link)))
        myfile.writelines(sorted(urls_list))
        myfile.flush()
    myfile.close()
    dividing_file(file_name, 0)
    return last_date


def call_exit():
    used_dates = [file for file in listdir(current_file_dir + '/data/') if file.startswith('last_used_date_')]
    list_last_date = set()
    for i in range(len(used_dates)):
        f = open(current_file_dir + '/data/last_used_date_' + str(i) + '.txt', 'r', encoding='utf-8')
        list_last_date.add([x.strip() for x in f.readlines()][0])
        f.close()
        try:
            remove(current_file_dir + '/data/last_used_date_' + str(i) + '.txt')
        except OSError:
            print('Could not remove file : ')
    max_date = max(list_last_date)
    # last_date_file = open(current_file_dir + '/data/last_used_date.txt', 'w', encoding='utf-8')
    config = Configs.objects.get(pk=1)
    config.last_used_date = max_date
    config.save()
    # last_date_file.write(max_date)
    # last_date_file.flush()
    # last_date_file.close()


# class Command(BaseCommand):
#     help = 'Scrapping Shops'
#
#     def handle(self, *args, **options):
#         sys.stdout.write('Start scrapping Shops.\n')
#         self.scrap()
#         sys.stdout.write('\n')

    # @staticmethod
def main():
    try:
        my_dirs = ['/data/output/', '/data/temp/', '/data/input/']
        full_dirs = []
        for my_dir in my_dirs:
            full_dirs.append(current_file_dir + my_dir)
        for my_full_dir in full_dirs:
            if not path.exists(my_full_dir):
                makedirs(my_full_dir, 0o777)
            else:
                sys.stdout.write(
                    'Directory {} with that name already exist continuing\n'.format(my_full_dir.split('/')[-1]))
    except IOError:
        pass
    sys.stdout.write('Calling get initial data')
    last_date = get_initial_data()
    if read_input_files() > 0:
        threads = 0
        while True:
            try:
                threads = int(input(template("How Many Threads To use ? type here : ")))
            except ValueError:
                print(template("Sorry, I didn't understand that."))
                continue
            else:
                break
        bots = [Scrapify(x, threads, last_date) for x in range(0, threads)]
        for bot in bots:
            bot.start()
            sleep(2)
        # waiting all bots to finish
        for bot in bots:
            bot.join()
        # print('Calling atexit.register')
        # call_exit()
        # insert_shops = InsertShops()
        # try:
        #     insert_shops.insert()
        # except Exception as e:
        #     sys.stdout.write('{}.\n'.format(e))


if __name__ == '__main__':
    main()
    atexit.register(call_exit)

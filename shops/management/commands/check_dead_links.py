import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopify_tracker_backend.settings')
django.setup()

from shops.models import Shops
import urllib.request
import requests
from threading import Thread
from requests.exceptions import RequestException
from time import sleep
from django.core.paginator import Paginator


class Styles:
    colors = [
        '\033[1;30m', '\033[1;31m', '\033[1;32m', '\033[1;33m', '\033[1;34m',
        '\033[1;35m', '\033[1;36m', '\033[1;37m', '\033[90m', '\033[92m',
        '\033[1;41m', '\033[1;42m', '\033[1;43m', '\033[1;44m', '\033[1;45m',
        '\033[1;46m', '\033[1;47m', '\033[0;30;47m', '\033[0;31;47m', '\033[0;32;47m',
        '\033[0;33;47m', '\033[0;34;47m', '\033[0;35;47m', '\033[0;36;47m'
    ]


class CheckDeadLinks(Thread):
    def __init__(self, color, threads, paginated):
        Thread.__init__(self)
        self.threads = threads
        self.color = color
        self.paginated = paginated

    def run(self):
        while self.paginated.page(int(self.color + 1)).has_next():
            ids_list = []
            for id_ in self.paginated.page(int(self.color + 1)).object_list:
                ids_list.append(id_.pk)
            shops = Shops.objects.filter(id__in=ids_list, availability=False).order_by('id')
            for shop in shops:
                if not shop.availability:
                    try:
                        response = requests.get(shop.shop_url, proxies=urllib.request.getproxies())
                        if response.status_code == 404 or response.status_code == 402:
                            shop.delete()
                            print(Styles.colors[self.color] + shop.shop_url + ' Deleted', '\033[0m')
                        elif response.ok:
                            shop.availability = True
                            shop.track_enabled = True
                            shop.save()
                            print(Styles.colors[self.color] + shop.shop_url + ' Response ok', '\033[0m')
                    except RequestException:
                        print(Styles.colors[self.color] + shop.shop_url + ' Request Exception Deleted', '\033[0m')
                        shop.delete()
                else:
                    print(Styles.colors[self.color] + shop.shop_url + " Was checked by another thread", '\033[0m')


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


def main():
    threads = 0
    while True:
        try:
            threads = int(input(template("How Many Threads To use ? type here 23: ")))
        except ValueError:
            print(template("Sorry, I didn't understand that."))
            continue
        else:
            break
    shops = Shops.objects.filter(availability=False).order_by('id')
    paginated = Paginator(shops, threads)
    bots = [CheckDeadLinks(x, threads, paginated) for x in range(0, threads)]
    for bot in bots:
        bot.start()
        sleep(2)
    # waiting all bots to finish
    for bot in bots:
        bot.join()


if __name__ == '__main__':
    main()

from __future__ import absolute_import, unicode_literals
from os import environ
from celery import Celery
# from celery.schedules import crontab
from django.conf import settings

environ.setdefault("DJANGO_SETTINGS_MODULE", "shopify_tracker_backend.settings")

app = Celery('Qaryb_API', broker=settings.CELERY_BROKER_URL)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.timezone = settings.TIME_ZONE
app.conf.setdefault('worker_cancel_long_running_tasks_on_connection_loss', True)
app.conf.task_serializer = 'pickle'
app.conf.result_serializer = 'pickle'
app.conf.accept_content = ['application/json', 'application/x-python-serialize']
# app.autodiscover_tasks(
#     packages=(
#         'account.base.tasks',
#         'offers.base.tasks',
#         'order.base.tasks',
#         'shop.base.tasks',
#         'chat.base.tasks',
#         'subscription.base.tasks',
#     )
# )

# app.conf.beat_schedule = {
#     # Executes every Midnight
#     'inform-indexed-articles': {
#         'task': 'shop.base.tasks.base_inform_indexed_articles',
#         'schedule': crontab(hour=0, minute=0),
#     },
# }


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # Executes every day at midnight
#     sender.add_periodic_task(
#         crontab(hour=23, minute=59),
#         base_inform_indexed_articles.s(),
#     )


# @app.task(bind=True, serializer='json')
# def base_inform_indexed_articles(self):
#     # Fixes Apps aren't loaded yet
#     from subscription.models import IndexedArticles
#
#     indexed_articles = IndexedArticles.objects.filter(email_informed=False).all()
#     host = 'smtp.gmail.com'
#     port = 587
#     username = 'no-reply@qaryb.com'
#     password = '24YAqua09'
#     use_tls = True
#     mail_subject = f'Nouveau articles référencés'
#     mail_template = 'inform_new_indexed_articles.html'
#     message = render_to_string(mail_template, {
#         'articles': indexed_articles,
#         'front_domain': f"{config('FRONT_DOMAIN')}",
#     })
#     with get_connection(host=host,
#                         port=port,
#                         username=username,
#                         password=password,
#                         use_tls=use_tls) as connection:
#         email = EmailMessage(
#             mail_subject,
#             message,
#             to=('yousra@qaryb.com', 'n.hilale@qaryb.com'),
#             connection=connection,
#             from_email='no-reply@qaryb.com',
#         )
#         email.content_subtype = "html"
#         email.send(fail_silently=False)
#         indexed_articles.update(email_informed=True)

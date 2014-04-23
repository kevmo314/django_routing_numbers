from django.db.models.signals import post_syncdb
from django_routing_numbers.models import Institution
import django_routing_numbers.models

def post_syncdb_callback(sender, **kwargs):
	django_routing_numbers.models.Institution.objects.fetch_dataset()

post_syncdb.connect(post_syncdb_callback, sender=django_routing_numbers.models)

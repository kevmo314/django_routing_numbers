import requests

from django.test import TestCase
from models import Institution, InstitutionManager
from datetime import date, datetime

class TestInstitution(TestCase):
	def test_contents(self):
		lines = requests.get('http://www.fededirectory.frb.org/FedACHdir.txt').text.count('\n')
		self.assertEqual(Institution.objects.count(), lines)
		start = datetime.now()
		self.assertEqual(Institution.objects.get(routing_number='011000015').customer_name, "FEDERAL RESERVE BANK")
		self.assertLess((datetime.now() - start).seconds, 1)
		self.assertGreater(Institution.objects.filter(change_date__gte=date(2014,1,1)).count(), 0)
		Institution.objects.filter(change_date__gte=date(2014,1,1)).delete()
		self.assertIsNotNone(Institution.objects.all())
		self.assertEqual(lines, Institution.objects.count())
		Institution.objects.filter(routing_number='011000015').delete()
		self.assertEqual(lines - 1, Institution.objects.count())
		Institution.objects.filter(change_date__gte=date(2000,1,1)).delete()
		self.assertIsNotNone(Institution.objects.all())
		self.assertEqual(lines, Institution.objects.count())
		self.assertEqual(Institution.objects.get(routing_number='011000015').customer_name, "FEDERAL RESERVE BANK")
		

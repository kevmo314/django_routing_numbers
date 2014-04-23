import requests
from datetime import date, datetime

from django.db import models, transaction

class InstitutionManager(models.Manager):
	def get_queryset(self):
		qs = super(InstitutionManager, self).get_queryset()
		if qs.count() == 0:
			self.fetch_dataset()
		else:
			max = qs.aggregate(models.Max('change_date'))['change_date__max']
			if (date.today() - max).days > 1:
				self.fetch_dataset(start_date=max)
		return qs

	@transaction.atomic
	def fetch_dataset(self, start_date=None):
		if start_date:
			r = requests.post('http://www.fededirectory.frb.org/updatesForACH.cfm', {'sinceDate':start_date.strftime('%m/%d/%Y')})
		else:
			super(InstitutionManager, self).get_queryset().delete()
			r = requests.get('http://www.fededirectory.frb.org/FedACHdir.txt')
		if r.status_code != 200:
			raise Exception("Status code %d received" % r.status_code)
		if len(r.text) == 0 or r.text[0] == ' ':
			return # no data received
		for line in r.text.splitlines():
			institution = {}
			institution['routing_number'] = line[:9]
			institution['office_code'] = line[9]
			institution['servicing_frb_number'] = line[10:19]
			institution['record_type_code'] = line[19]
			institution['change_date'] = datetime.strptime(line[20:26], '%m%d%y').date()
			institution['new_routing_number'] = line[26:35]
			institution['customer_name'] = line[35:71].rstrip()
			institution['address'] = line[71:107].rstrip()
			institution['city'] = line[107:127].rstrip()
			institution['state_code'] = line[127:129]
			institution['zipcode'] = line[129:134]
			institution['zipcode_extension'] = line[134:138]
			institution['telephone_area_code'] = line[138:141]
			institution['telephone_prefix_number'] = line[141:144]
			institution['telephone_suffix_number'] = line[144:148]
			institution['institution_status_code'] = line[148]
			if start_date:
				super(InstitutionManager, self).get_queryset().get_or_create(routing_number=institution['routing_number'], defaults=institution)
			else:
				Institution(**institution).save()

class Institution(models.Model):
	objects = InstitutionManager()

	routing_number = models.CharField(max_length=9, help_text="The institution's routing number", primary_key=True)
	office_code = models.CharField(max_length=1, choices=(('O', 'main'), ('B', 'branch')), help_text="Main office or branch")
	servicing_frb_number = models.CharField(max_length=9, help_text="Servicing Fed's main office routing number")
	record_type_code = models.IntegerField(choices=((0, 'Institution is a Federal Reserve Bank'), (1, 'Send items to customer routing number'), (2, 'Send items to customer using new routing number field')), help_text="The code indicating the ABA number to be used to route or send ACH items to the RFI", default=0)
	change_date = models.DateField(help_text="Date of last change to CRF information", db_index=True)
	new_routing_number = models.CharField(max_length=9, help_text="Institution's new routing number resulting start_date a merger or renumber")
	customer_name = models.CharField(max_length=36, help_text="Commonly used abbreviated name", db_index=True)
	address = models.CharField(max_length=36, help_text="Delivery address")
	city = models.CharField(max_length=20, help_text="City name in the delivery address")
	state_code = models.CharField(max_length=2, help_text="State code of the state in the delivery address")
	zipcode = models.CharField(max_length=5, help_text="Zip code in the delivery address")
	zipcode_extension = models.CharField(max_length=4, help_text="Zip code extension in the delivery address")
	telephone_area_code = models.CharField(max_length=3, help_text="Area code of the CRF contact telephone number")
	telephone_prefix_number = models.CharField(max_length=3, help_text="Prefix of the CRF contact telephone number")
	telephone_suffix_number = models.CharField(max_length=4, help_text="Suffix of the CRF contact telephone number")
	institution_status_code = models.IntegerField(choices=((1, 'Receives Gov/Comm'),), help_text="Code is based on the customers receiver code", default=1)

	@property
	def telephone_number(self, fmt="(%s) %s-%s"):
		return fmt % (telephone_area_code, telephone_prefix_number, telephone_suffix_number)


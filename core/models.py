# This is an auto-generated Django model module created by ogrinspect.
API_TOKEN = 'ac1095d7aab642f359b8a83e4e56bf1ca7794b66e473eabde4cc34fb05d92902'
API_BASE = 'http://api1.chicagopolice.org/clearpath/api/1.0/'

from django.contrib.gis.db import models

from django.contrib.gis.measure import Distance

import xlrd, xlwt
import requests
from urlparse import urljoin
import json

CREATE_CONCERN_ENDPOINT = urljoin(API_BASE,'communityConcerns/create')
CHECK_CONCERN_ENDPOINT  = urljoin(API_BASE,'communityConcerns/status')
DEFAULT_DESCRIPTION = {
    'V': 'This building is vacant.',
    'DG': 'This building has drug and/or gang problems.'
}
WORKBOOK_HEADERS = ['building_id','street_number','street_dir','street_name','vacant','drug_gang','information']

def footprints_within(point,miles):
    distance = Distance(mi=miles)
    return Footprint.objects.filter(geom__distance_lte=(point,distance))

def make_new_workbook(footprints):
    book = xlwt.Workbook()
    sheet = book.add_sheet('Buildings')
    for i,col_name in enumerate(WORKBOOK_HEADERS):
        sheet.write(0, i, col_name)

    for i,fp in enumerate(footprints):
        i += 1
        sheet.write(i, 0, fp.building_id)
        if fp.to_address == fp.from_address:
            number = '%s' % fp.from_address
        else:
            number = '%s-%s' % (fp.from_address,fp.to_address)
        sheet.write(i, 1, number)
        sheet.write(i, 2, fp.street_prefix)
        sheet.write(i, 3, fp.street_name)
        sheet.write(i, 4, '') # vacant
        sheet.write(i, 5, '') # drug/gang
        sheet.write(i, 6, '') # description
    book.save('/tmp/foo.xls')

def process_workbook(filename,reporter_email='joe@germuska.com'):
    book = xlrd.open_workbook(filename)
    result = {
        'concerns': [],
        'errors': [],
    }
    sheet = book.sheet_by_index(0) # for now assume always first sheet and that it is formatted correctly.
    for i in range(1,sheet.nrows):
        vacant = sheet.cell_value(i,4)
        drug_gang = sheet.cell_value(i,5)
        if vacant or drug_gang:
            building_id = sheet.cell_value(i,0)
            footprint = Footprint.objects.get(building_id=building_id)
            description = sheet.cell_value(i,6)
            trouble_types = []
            if vacant:
                trouble_types.append('V')
            if drug_gang:
                trouble_types.append('DG')
            for tt in trouble_types:
                concern = Concern(footprint=footprint,trouble_type=tt,reporter_email=reporter_email)
                if description:
                    concern.description = description
                else:
                    concern.description = DEFAULT_DESCRIPTION[tt]
                concern.save()
                try:
                    report_concern(concern)
                    result['concerns'].append(concern)
                except Exception, e:
                    result['errors'].append((concern,e))
    return result
    
class Footprint(models.Model):
    building_id = models.IntegerField()
    cdb_city_i = models.CharField(max_length=12)
    status = models.CharField(max_length=12)
    from_address = models.IntegerField(null=True)
    to_address = models.IntegerField(null=True)
    street_prefix = models.CharField(max_length=1)
    street_name = models.CharField(max_length=35)
    street_type = models.CharField(max_length=5)
    unit_name = models.CharField(max_length=8)
    non_standard = models.CharField(max_length=8)
    name1 = models.CharField(max_length=50)
    name2 = models.CharField(max_length=50)
    comments = models.CharField(max_length=50)
    stories = models.IntegerField(null=True)
    orig_bldg_field = models.IntegerField(null=True)
    footprint_field = models.CharField(max_length=15)
    create_user = models.CharField(max_length=7)
    create_date = models.DateField(null=True)
    active_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    demolished = models.DateField(null=True)
    edit_date = models.DateField(null=True)
    edit_userid = models.CharField(max_length=7)
    edit_source = models.CharField(max_length=15)
    qc_date = models.DateField(null=True)
    qc_userid = models.CharField(max_length=7)
    qc_source = models.CharField(max_length=10)
    x_coord = models.FloatField(null=True)
    y_coord = models.FloatField(null=True)
    z_coord = models.IntegerField(null=True)
    harris_str = models.CharField(max_length=14)
    no_of_units = models.IntegerField(null=True)
    no_stories = models.IntegerField(null=True)
    year_built = models.IntegerField(null=True)
    square_footage = models.FloatField(null=True)
    condition = models.CharField(max_length=18)
    condition_date = models.DateField(null=True)
    vacancy_status = models.CharField(max_length=1)
    label_hous = models.CharField(max_length=15)
    suffix_dir = models.CharField(max_length=10)
    shape_area = models.FloatField(null=True)
    shape_len = models.FloatField(null=True)
    geom = models.MultiPolygonField(srid=3435)
    objects = models.GeoManager()

    @property
    def display_address(self):
        parts = []
        if self.from_address != self.to_address:
            parts.append('%s-%s' % (self.from_address,self.to_address))
        else:
            parts.append(self.from_address)
        parts.extend([self.street_prefix, self.street_name, self.street_type])    
        return u' '.join(map(unicode,parts))

    def __unicode__(self):
        return self.display_address


CLASSIFICATION_CHOICES = (
    ('GANGS', 'Gangs'),
    ('NARC', 'Narcotics'),
    ('PROSTIT', 'Prostitution'),
    ('OTHER', 'Other Criminal or Disorder Activity'),
    ('PBLDG', 'Troubled Building'),
)

TROUBLE_TYPE_CHOICES = (
    ('V', 'Vacant'),
    ('DG', 'Drug and Gang'),
)

class Concern(models.Model):
    """(Concern description)"""
    classification = models.CharField(choices=CLASSIFICATION_CHOICES, default='PBLDG', max_length=7)
    trouble_type = models.CharField(choices=TROUBLE_TYPE_CHOICES, max_length=2)
    description = models.TextField()
    reporter_email = models.EmailField()
    incident_date = models.DateTimeField(auto_now_add=True)
    footprint = models.ForeignKey(Footprint)
    concern_id = models.IntegerField(blank=True, null=True)
    pin_number = models.CharField(blank=True, max_length=7)
    status = models.CharField(blank=True, max_length=20)
    closed_date = models.DateField(blank=True, null=True, auto_now_add=False)
    public_response = models.TextField(blank=True)

    class Meta:
        ordering = []
        verbose_name, verbose_name_plural = "", "s"

    def __unicode__(self):
        return u"Concern"

    @models.permalink
    def get_absolute_url(self):
        return ('Concern', [self.id])
        
def report_concern(concern):
    """Reports concern using API and updates with response information
    communityConcernClassification
    troubleType
    description
    reporterEmailAddress
    incidentDate
    incidentFromTime
    incidentToTime
    incidentStreetNo
    incidentStreetDirection
    incidentStreetName
    incidentAptNo
    incidentBuildingType
    incidentBuildingName
    incidentBuildingFloor
    incidentBuildingUnit
    incidentLocationDescription
    lat
    lng
    """

    data = {
        'apiToken': API_TOKEN,
        'communityConcernClassification': concern.classification,
        'troubleType': concern.trouble_type,
        'description': concern.description,
        'reporterEmailAddress': concern.reporter_email,
        'incidentDate': concern.incident_date.strftime('%m-%d-%Y'),
        'incidentFromTime': concern.incident_date.strftime('%H%M'),
        'incidentStreetNo': concern.footprint.from_address,
        'incidentStreetDirection': concern.footprint.street_prefix,
        'incidentStreetName': concern.footprint.street_name,
        'incidentBuildingType': 'OTHER',
        'incidentBuildingName': '(not null)',
        'incidentBuildingFloor': '(not null)',
        'incidentBuildingUnit': '(not null)',
    }
    print data
    response = requests.post(CREATE_CONCERN_ENDPOINT,data=data)
    # check response status is ok
    print response.content
    response_data = json.loads(response.content)
    if response_data.has_key('error'):
        print response_data['error']
        raise Exception()
        
    concern.concern_id = response_data['concernId']
    concern.pin_number = response_data['pinNumber']
    concern.status = response_data['status']
    concern.save()

def check_concern_status(concern):
    pass

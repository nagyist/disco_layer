from django.db import models

class Agency(models.Model):
    acronym = models.CharField(max_length=128)
    def __unicode__(self):
        return self.acronym

class SubService(models.Model):
    cat_id = models.CharField(max_length=512)
    desc = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=512, null=True, blank=True)
    info_url = models.CharField(max_length=512, null=True, blank=True)
    primary_audience = models.CharField(max_length=512, null=True, blank=True)
    agency = models.ForeignKey(Agency, default=1)

    def __unicode__(self):
        return self.name

class ServiceTag(models.Model):
    label = models.CharField(max_length=512)
    def __unicode__(self):
        return self.label

class LifeEvent(models.Model):
    label = models.TextField()
    def __unicode__(self):
        return self.label

class ServiceType(models.Model):
    label = models.TextField()
    def __unicode__(self):
        return self.label

class Service(models.Model):
    old_src_id = models.IntegerField(null=True, blank=True)
    src_id  = models.CharField(max_length=256, null=True, blank=True)
    org_acronym  = models.CharField(max_length=64, null=True, blank=True)
    json_filename  = models.CharField(max_length=512, null=True, blank=True)
    info_url = models.CharField(max_length=512, null=True, blank=True)
    name = models.CharField(max_length=512, null=True, blank=True)
    acronym = models.CharField(max_length=512, null=True, blank=True)
    tagline = models.CharField(max_length=512, null=True, blank=True)
    primary_audience = models.CharField(max_length=512, null=True, blank=True)
    analytics_available = models.CharField(max_length=512, null=True, blank=True)
    incidental = models.CharField(max_length=512, null=True, blank=True)
    secondary = models.CharField(max_length=512, null=True, blank=True)
    src_type = models.CharField(max_length=512, null=True, blank=True)
    description  = models.TextField(null=True, blank=True)
    comment  = models.TextField(null=True, blank=True)
    current = models.CharField(max_length=512, null=True, blank=True)
    service_types = models.ManyToManyField(ServiceType)
    service_tags =  models.ManyToManyField(ServiceTag)
    life_events =  models.ManyToManyField(LifeEvent)
    agency = models.ForeignKey(Agency, default=1)

    def __unicode__(self):
        return "%s: %s: %s" % (self.agency.acronym, self.src_id, self.name)


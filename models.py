#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import datetime

from django.db import models

from rapidsms.models import ExtensibleModelBase
from rapidsms.models import Contact
from rapidsms.contrib.locations.models import Location

from logistics.models import Commodity #LOGISTICS
from logistics.models import Shipment #LOGISTICS

class SupplyBase(models.Model):
    # TODO just link to a commodity?
    commodity = models.ForeignKey(Commodity, blank=True, null=True) #LOGISTICS

    # TODO and/or duplicate most of its fields here (optionally)

    # might be worth duplicating, because units and dimensions
    # may be different for shipping container vs storage container
    UNIT_CHOICES = (
        ('PL', 'pallets'),
        ('TM', 'Tons (metric)'),
        ('KG', 'Kilograms'),
        ('BX', 'Boxes'),
        ('TB', 'Tiny boxes'),
        ('BL', 'Bales'),
        ('LT', 'Liters'),
        ('CN', 'Containers'),
        ('DS', 'Doses'),
        ('VI', 'Vials'),
        ('SA', 'Sachets'),
        ('BG', 'Bags'),
        ('BT', 'Bottles'),
        ('UK', 'Unknown'),
    )
    name = models.CharField(max_length=160, blank=True, null=True)
    slug = models.CharField(max_length=20, unique=True)
    # List of alternate spellings, abbreviations, etc that can be specified
    # via webui. eg, enter books, book for object where slug=textbooks
    aliases = models.CharField(max_length=160, blank=True, null=True,\
        help_text="List of alternate spellings, abbreviations, etc. Separate each alias with a single comma and no spaces.")

    # unit of supply for storage purposes
    unit = models.CharField(max_length=3, choices=UNIT_CHOICES)

    # per unit storage volume and weight
    volume = models.CharField(max_length=160, blank=True, null=True)
    weight = models.CharField(max_length=160, blank=True, null=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    def alias_list(self):
        ''' Returns a list of self.aliases '''
        if self.aliases is not None:
            return self.aliases.split(',')
        else:
            return None

    def has_alias(self, term):
        ''' Checks whether a search term is in a supply's list
            of aliases. Returns None if supply has no aliases,
            and True or False otherwise. '''
        if self.aliases is not None:
            alias_list = self.alias_list()
            if term in alias_list:
                return True
            else:
                return False
        else:
            return None

class Supply(SupplyBase):
    ''' Stuff '''
    __metaclass__ = ExtensibleModelBase

class StockLevelBase(models.Model):
    quantity = models.CharField(max_length=160)
    datetime = models.DateTimeField(default=datetime.datetime.utcnow)
    
    class Meta:
        abstract = True

class StockLevel(StockLevelBase):
    ''' Amount of one supply at a certain time '''
    __metaclass__ = ExtensibleModelBase

class StockBase(models.Model):
    stock_levels = models.ManyToManyField(StockLevel, blank=True, null=True)
    supply = models.ForeignKey(Supply)
    
    class Meta:
        abstract = True

class Stock(StockBase):
    ''' Amounts of one supply over time'''
    __metaclass__ = ExtensibleModelBase

class InventoryBase(models.Model):
    stocks = models.ManyToManyField(Stock, blank=True, null=True)
    location = models.ForeignKey(Location)
    
    class Meta:
        abstract = True

class Inventory(InventoryBase):
    ''' Supplies stored at a location '''
    __metaclass__ = ExtensibleModelBase

class TransactionBase(models.Model):
    TRANSACTION_CHOICES = (
        ('R', 'Receipt'),
        ('I', 'Issuance'),
        ('S', 'Spoilage'),
        ('L', 'Loss'),
        ('T', 'Theft'),
        ('F', 'Found'),
        ('U', 'Unknown'),
    )
    type = models.CharField(max_length=3, choices=TRANSACTION_CHOICES)
    quantity = models.CharField(max_length=160)
    datetime = models.DateTimeField(default=datetime.datetime.utcnow)
    stock = models.ForeignKey(Stock)
    
    class Meta:
        abstract = True

class Transaction(TransactionBase):
    ''' Addition or deduction of stock from inventory '''
    __metaclass__ = ExtensibleModelBase

class ConsignmentBase(models.Model):
    consignor = models.ForeignKey(Contact, help_text="Person issuing stock")
    consignee = models.ForeignKey(Contact, help_text="Person receiving stock")
    transaction = models.ForeignKey(Transaction)

    #TODO should this be ShipmentSighting instead?
    shipment = models.ForeignKey(Shipment, blank=True, null=True) #LOGISTICS
    
    class Meta:
        abstract = True

class Consignment(ConsignmentBase):
    ''' Consignment of stock from one party to another '''
    __metaclass__ = ExtensibleModelBase

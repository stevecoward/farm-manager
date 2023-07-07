from datetime import datetime
from . import BaseModel
from peewee import CharField, DoubleField, TextField, ForeignKeyField, DateField, IntegerField, BooleanField, DateTimeField


class GameConfig(BaseModel):
    days_in_month = IntegerField(null=False)


class Maps(BaseModel):
    name = CharField(unique=True)


class Farms(BaseModel):
    name = CharField(unique=True)
    map = ForeignKeyField(Maps, backref='farms')


class Fields(BaseModel):
    name = CharField()
    acreage = DoubleField()
    yield_potential = DoubleField()
    crop = TextField(choices=['wheat', 'barley', 'canola', 'oat', 'corn', 'sunflowers', 'soybeans', 'potatoes', 'sugar_beet', 'sugarcane', 'cotton', 'sorghum', 'grapes', 'olives', 'grass', 'oilseed_radish'])
    action = TextField(choices=['harvest', 'forage'])
    farm = ForeignKeyField(Farms, backref='farm')
    notes = CharField(null=True)
    precision_before = IntegerField(null=True)
    precision_after = IntegerField(null=True)

    class Meta:
        indexes = ((('name', 'farm'), True),)


class CropCalendars(BaseModel):
    crop_name = CharField(null=False)
    sow_start = IntegerField()
    sow_end = IntegerField()
    harvest_start = IntegerField()
    harvest_end = IntegerField()
    map = ForeignKeyField(Maps, backref='calendars')

    class Meta:
        indexes = ((('map', 'crop_name'), True),)


class Workers(BaseModel):
    name = CharField(unique=True)
    role = TextField(choices=['transport', 'auger', 'operator', 'production'])


class WorkerFarms(BaseModel):
    worker = ForeignKeyField(Workers, backref='worker')
    farm = ForeignKeyField(Farms, backref='farm')

    class Meta:
        indexes = ((("worker", "farm"), True),)


class WorkTasks(BaseModel):
    name = TextField(choices=['till', 'hoe', 'weed', 'sow', 'harvest', 
                                    'forage', 'spread_fertilizer', 'spread_herbicide', 
                                    'spread_lime', 'roll', 'product_fill', 'product_empty', 
                                    'silo_load', 'silo_unload', 'animals_feed', 'animals_bedding', 
                                    'transport', 'transport_auger'
                                   ])
    category = TextField(choices=['field', 'grassland', 'production', 'animal'])


class WorkOrders(BaseModel):
    created = DateTimeField(default=datetime.now)
    farm = ForeignKeyField(Farms, backref='farm')
    field = ForeignKeyField(Fields, backref='field')
    worker = ForeignKeyField(Workers, backref='worker')
    tasks = CharField()
    completed = DateTimeField(null=True)

    # class Meta:
    #     indexes = ((("created", "farm", "field", "worker"), True),)


class WorkerAssignments(BaseModel):
    started = DateTimeField(default=datetime.now)
    work_order = ForeignKeyField(WorkOrders, backref='work_order')
    task = ForeignKeyField(WorkTasks)
    completed = DateTimeField(null=True)
    notes = CharField(null=True)
    month_assigned = IntegerField(null=True)


class FieldYields(BaseModel):
    field = ForeignKeyField(Fields, backref='field')
    assignment = ForeignKeyField(WorkerAssignments, backref='assignment')
    amount_yield = DoubleField()

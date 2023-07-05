from enum import Enum


class FieldsActionEnum(str, Enum):
    harvest = 'harvest'
    forage = 'forage'


class WorkersRoleEnum(str, Enum):
    transport = 'transport'
    auger = 'auger'
    operator = 'operator'
    production = 'production'
    any = 'any'


class FieldsCropEnum(str, Enum):
    wheat = 'wheat'
    barley = 'barley'
    canola = 'canola'
    oat = 'oat'
    corn = 'corn'
    sunflowers = 'sunflowers'
    soyboeans = 'soybeans'
    potatoes = 'potatoes'
    sugar_beet = 'sugar_beet'
    sugarcane = 'sugarcane'
    cotton = 'cotton'
    sorghum = 'sorghum'
    grapes = 'grapes'
    olives = 'olives'
    grass = 'grass'
    oilseed_radish = 'oilseed_radish'


class WorkerAssignmentsEnum(str, Enum):
    till = 'till'
    hoe = 'hoe'
    weed = 'weed'
    sow = 'sow'
    harvest = 'harvest'
    forage = 'forage'
    spread_fertilizer = 'spread_fertilizer'
    spread_herbicide = 'spread_herbicide'
    spread_lime = 'spread_lime'
    roll = 'roll'
    product_fill = 'product_fill'
    product_empty = 'product_empty'
    silo_load = 'silo_load'
    silo_unload = 'silo_unload'
    animals_feed = 'animals_feed'
    animals_bedding = 'animals_bedding'
    transport = 'transport'
    transport_auger = 'transport_auger'

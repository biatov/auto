# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AutoItem(scrapy.Item):
    image = scrapy.Field()
    description = scrapy.Field()
    auction_date = scrapy.Field()
    actual_cash_value = scrapy.Field()
    repair_cost = scrapy.Field()
    odometer = scrapy.Field()
    prim_damage = scrapy.Field()
    sec_damage = scrapy.Field()
    price_sold_or_highest_bid = scrapy.Field()

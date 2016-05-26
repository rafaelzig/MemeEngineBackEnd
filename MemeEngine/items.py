# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Meme(scrapy.Item):
	# define the fields for your item here like:
	# name = scrapy.Field()
	id = scrapy.Field()
	source = scrapy.Field()
	title = scrapy.Field()
	caption = scrapy.Field()
	name = scrapy.Field()
	score = scrapy.Field()
	url = scrapy.Field()

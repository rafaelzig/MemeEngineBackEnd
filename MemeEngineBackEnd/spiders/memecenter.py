# -*- coding: utf-8 -*-
import scrapy

from MemeEngineBackEnd.items import Meme

SUFFIX = "/page/"
IMAGE_DATA_TYPE = '1'


class MemeCenterSpider(scrapy.Spider):
	name = "MemeCenter"
	allowed_domains = ["memecenter.com"]
	start_urls = ["http://www.memecenter.com" + SUFFIX + '1']

	def parse(self, response):
		for post in response.xpath("//div[@class='content  ']"):
			if post.xpath("./@data-type").extract_first() == IMAGE_DATA_TYPE:  # Skip videos and gifs
				meme = Meme()
				meme["source"] = self.allowed_domains[0]
				meme["name"] = ""
				meme["caption"] = ""
				meme["url"] = post.xpath("./div[1]/a/@href").extract_first()
				meme["id"] = post.xpath("./@data-id").extract_first()
				temp = post.xpath(".//img[@class='rrcont']")
				meme["title"] = temp.xpath("./@alt").extract_first()
				meme["image"] = temp.xpath("./@src").extract_first()
				meme["score"] = post.xpath(".//div[@class='like act_like']/div[2]/span/text()").extract_first()
				yield meme
		url = response.url.split('/')
		url = response.urljoin(SUFFIX + str(int(url[len(url) - 1]) + 1))
		yield scrapy.Request(url, self.parse)

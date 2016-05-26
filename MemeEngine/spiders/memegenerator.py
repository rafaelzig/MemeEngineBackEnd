# -*- coding: utf-8 -*-
import scrapy

from MemeEngine.items import Meme


class MemeGeneratorSpider(scrapy.Spider):
	name = "MemeGenerator"
	allowed_domains = ["memegenerator.net"]
	start_urls = ["https://memegenerator.net/images/new/week"]

	def parse(self, response):
		for post in response.xpath("//div[@class='item_medium_small display-hover-container']"):
			meme = Meme()
			meme["source"] = self.allowed_domains[0]
			temp = post.xpath(".//div[@class='voter horizontal']")
			meme["id"] = temp.xpath("./@data-entity-id").extract()[0]
			meme["score"] = temp.xpath(".//div[@class='score']/text()").re("\d+")[0]
			temp = post.xpath("./a/img")
			meme["url"] = temp.xpath("./@src").extract()[0].replace("250x250", "500x")
			temp = temp.xpath("./@alt").extract()[0].split(" - ")
			meme["name"] = temp[0]
			meme["caption"] = temp[1]
			yield meme
		temp = response.xpath("//ul[@class='pager']/li/a")
		next_page = temp[len(temp) - 1].xpath("./@href")
		if next_page:
			url = response.urljoin(next_page.extract()[0])
			yield scrapy.Request(url, self.parse)

# -*- coding: utf-8 -*-
import scrapy

from MemeEngineBackEnd.items import Meme


class MemeGeneratorSpider(scrapy.Spider):
	name = "MemeGenerator"
	# isAlive = True
	allowed_domains = ["memegenerator.net"]
	start_urls = ["https://memegenerator.net/images/new/week"]

	def parse(self, response):
		for post in response.xpath("//div[@class='item_medium_small display-hover-container']"):
			# if self.isAlive:
				meme = Meme()
				meme["title"] = ""
				meme["source"] = self.allowed_domains[0]
				meme["url"] = response.urljoin(post.xpath("./a/@href").extract_first())
				temp = post.xpath(".//div[@class='voter horizontal']")
				meme["id"] = temp.xpath("./@data-entity-id").extract_first()
				meme["score"] = temp.xpath(".//div[@class='score']/text()").re("\d+")[0]
				temp = post.xpath("./a/img")
				meme["image"] = temp.xpath("./@src").extract_first().replace("250x250", "500x")
				temp = temp.xpath("./@alt").extract_first().split(" - ")
				meme["name"] = temp[0]
				meme["caption"] = temp[1]
				yield meme
		# else:
		# 	raise CloseSpider(reason="Previously crawled content found.")
		temp = response.xpath("//ul[@class='pager']/li/a")
		next_page = temp[len(temp) - 1].xpath("./@href")
		if next_page:
			url = response.urljoin(next_page.extract_first())
			yield scrapy.Request(url, self.parse)

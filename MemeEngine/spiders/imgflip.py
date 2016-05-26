# -*- coding: utf-8 -*-
import scrapy

from MemeEngine.items import Meme


class ImgFlipSpider(scrapy.Spider):
	name = "ImgFlip"
	allowed_domains = ["imgflip.com"]
	start_urls = ["https://imgflip.com/?sort=latest&tgz=memes"]

	def parse(self, response):
		for post in response.xpath("//div[@class='base-unit clearfix']"):
			meme = Meme()
			meme["source"] = self.allowed_domains[0]
			meme["id"] = post.xpath(".//div[@class='img-flag']/@data-iid").extract()[0]
			temp = post.xpath(".//img[@class='base-img']")
			meme["url"] = "https:" + temp.xpath("./@src").extract()[0]
			temp = temp.xpath("./@alt").extract()[0].split(" | ")
			meme["name"] = temp[0]
			meme["caption"] = temp[1]
			temp = post.xpath(".//div[@class='base-view-count']/text()").re("(\d+)\s(?:upvote)")
			meme["score"] = temp[0] if temp else 0
			yield meme
		next_page = response.xpath("//a[@class='pager-next l but']/@href")
		if next_page:
			url = response.urljoin(next_page.extract()[0])
			yield scrapy.Request(url, self.parse)

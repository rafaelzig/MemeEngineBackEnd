# -*- coding: utf-8 -*-
import scrapy

from MECrawlerIndexer.items import Meme


class ImgFlipSpider(scrapy.Spider):
	name = "ImgFlip"
	allowed_domains = ["imgflip.com"]
	start_urls = ["https://imgflip.com/?sort=latest&tgz=memes"]

	def parse(self, response):
		for post in response.xpath("//div[@class='base-unit clearfix']"):
			meme = Meme()
			meme["source"] = self.allowed_domains[0]
			meme["title"] = ""
			meme["id"] = post.xpath(".//div[@class='img-flag']/@data-iid").extract_first()
			temp = post.xpath(".//a[@class='base-img-link']")
			meme["url"] = response.urljoin(temp.xpath("./@href").extract_first())
			temp = temp.xpath(".//img[@class='base-img']")
			meme["image"] = response.urljoin(temp.xpath("./@src").extract_first())
			temp = temp.xpath("./@alt").extract()[0].split(" | ")
			meme["name"] = temp[0]
			meme["caption"] = temp[1]
			temp = post.xpath(".//div[@class='base-view-count']/text()").re("(\d+)\s(?:upvote)")
			meme["score"] = temp[0] if temp else "0"
			yield meme
		next_page = response.xpath("//a[@class='pager-next l but']/@href")
		if next_page:
			url = response.urljoin(next_page.extract_first())
			yield scrapy.Request(url, self.parse)

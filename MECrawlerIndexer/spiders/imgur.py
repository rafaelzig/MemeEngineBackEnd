# -*- coding: utf-8 -*-
import scrapy

from MECrawlerIndexer.items import Meme

SUFFIX = "/t/memes/time/page/"


class ImgUrSpider(scrapy.Spider):
	name = "ImgUr"
	allowed_domains = ["imgur.com"]
	start_urls = ["http://imgur.com" + SUFFIX + '0']

	def parse(self, response):
		for post in response.xpath("//div[@class='post']"):
			if post.xpath(".//div[@class='post-info']/text()").re("image"):
				url = response.urljoin(post.xpath("./a/@href").extract_first())
				yield scrapy.Request(url, callback=self.parse_meme)
		url = response.url.split('/')
		url = response.urljoin(SUFFIX + str(int(url[len(url) - 1]) + 1))
		yield scrapy.Request(url, self.parse)

	def parse_meme(self, response):
		temp = response.xpath("/html/head/meta[@name='description']/@content").extract_first().split(" Meme: ")
		if len(temp) > 1:  # If meme has detailed info
			meme = Meme()
			meme["name"] = temp[0]
			meme["caption"] = temp[1]
			meme["url"] = response.url
			meme["source"] = self.allowed_domains[0]
			meme["id"] = response.xpath("//div[@class='post-image-container']/@id").extract_first()
			meme["score"] = response.xpath("//span[@class='points-" + meme["id"] + "']/text()").extract_first()
			temp = response.xpath("/html/head")
			meme["title"] = temp.xpath("./meta[@property='og:title']/@content").extract_first()
			meme["image"] = temp.xpath("./link[@rel='image_src']/@href").extract_first()
			yield meme

# -*- coding: utf-8 -*-
import scrapy
from scrapy.exceptions import CloseSpider

from MemeEngineBackEnd.items import Meme


class MemestacheSpider(scrapy.Spider):
	name = "Memestache"
	isAlive = True
	allowed_domains = ["memestache.com"]
	start_urls = ["http://www.memestache.com"]

	def parse(self, response):
		for post in response.xpath("//div[@class='post']"):
			if self.isAlive:
				if not post.xpath(".//input[@value='[Connect to Facebook to view this post]']"):
					temp = post.xpath(".//a[@class='surprise']/@href").extract()
					if temp:  # If it's not a video post
						meme = Meme()
						meme["url"] = temp[0]
						meme["source"] = self.allowed_domains[0]
						meme["id"] = post.xpath("./@id").re("\d+")[0]
						temp = post.xpath(".//input[@type='hidden']")
						meme["title"] = temp[0].xpath("./@value").extract_first()
						meme["caption"] = " ".join(
							temp[1].xpath("./@value").extract() + temp[2].xpath("./@value").extract())
						meme["image"] = post.xpath(".//div[@class='std_img']/a/img/@src").extract_first()
						temp = post.xpath(".//div[@class='post_footer_right']")
						meme["score"] = temp.xpath("./div[1]").re("\d+")[0]
						meme["name"] = temp.xpath("./div[2]/b/a/text()").extract_first()
						yield meme
			else:
				raise CloseSpider(reason="Previously crawled content found.")
		next_page = response.xpath("//div[@class='big']/a/@href")
		if next_page:
			url = response.urljoin(next_page.extract_first())
			yield scrapy.Request(url, self.parse)

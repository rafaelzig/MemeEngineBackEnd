# -*- coding: utf-8 -*-
import scrapy

from MemeEngine.items import Meme


class MemestacheSpider(scrapy.Spider):
	name = "Memestache"
	allowed_domains = ["memestache.com"]
	start_urls = ["http://www.memestache.com/"]

	def parse(self, response):
		for post in response.xpath("//div[@class='post']"):
			if not post.xpath("//input[@value='[Connect to Facebook to view this post]']"):
				meme = Meme()
				meme["source"] = self.allowed_domains[0]
				meme["id"] = post.xpath("./@id").re("\d+")[0]
				temp = post.xpath(".//input[@type='hidden']")
				meme["title"] = temp[0].xpath("./@value").extract()[0]
				meme["caption"] = " ".join(temp[1].xpath("./@value").extract() + temp[2].xpath("./@value").extract())
				meme["url"] = post.xpath(".//div[@class='std_img']/a/img/@src").extract()[0]
				temp = post.xpath(".//div[@class='post_footer_right']")
				meme["score"] = temp.xpath("./div[1]").re("\d+")[0]
				meme["name"] = temp.xpath("./div[2]/b/a/text()").extract()[0]
				yield meme
		next_page = response.xpath("//div[@class='big']/a/@href")
		if next_page:
			url = response.urljoin(next_page.extract()[0])
			yield scrapy.Request(url, self.parse)

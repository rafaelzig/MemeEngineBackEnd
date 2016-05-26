# -*- coding: utf-8 -*-
import scrapy

from MemeEngine.items import Meme


class QuickMemeSpider(scrapy.Spider):
	name = "QuickMeme"
	allowed_domains = ["quickmeme.com"]
	start_urls = ["http://www.quickmeme.com/new"]

	def parse(self, response):
		for post in response.xpath("//div[@class='post']"):
			temp = post.xpath(".//div[@class='cat-info']/ul/li/a")
			if temp.xpath("./@href").re("memes"):  # If it is a meme
				meme = Meme()
				meme["name"] = temp.xpath("./span/text()").extract()[0]
				meme["source"] = self.allowed_domains[0]
				meme["id"] = post.xpath("./@id").re("\d+")[0]
				meme["title"] = post.xpath(".//h2[@class='post-title']/a/text()").extract()[0]
				temp = post.xpath(".//img[@class='post-image']")
				meme["caption"] = temp.xpath("./@alt").extract()[0].split(" " + meme["name"])[0]
				meme["url"] = temp.xpath("./@src-nsfw").extract()[0] if temp.xpath("./@src-nsfw") else \
					temp.xpath("./@src").extract()[0]
				meme["score"] = "".join(post.xpath(".//div[@class='sharecounts']/p//text()").re("\d+"))
				yield meme
		next_page = response.xpath("//a[@id='page-next']/@href")
		if next_page:
			url = response.urljoin(next_page.extract()[0])
			yield scrapy.Request(url, self.parse)

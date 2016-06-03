# -*- coding: utf-8 -*-
import scrapy

from MemeEngineBackEnd.items import Meme


class QuickMemeSpider(scrapy.Spider):
	name = "QuickMeme"
	# isAlive = True
	allowed_domains = ["quickmeme.com"]
	start_urls = ["http://www.quickmeme.com/new"]

	def parse(self, response):
		for post in response.xpath("//div[@class='post']"):
			# if self.isAlive:
				temp = post.xpath(".//div[@class='cat-info']/ul/li/a")
				if temp.xpath("./@href").re("memes"):  # If it is a meme
					meme = Meme()
					meme["url"] = response.urljoin(post.xpath("./a/@href").extract_first())
					meme["name"] = temp.xpath("./span/text()").extract_first()
					meme["source"] = self.allowed_domains[0]
					meme["id"] = post.xpath("./@id").re("\d+")[0]
					meme["title"] = post.xpath(".//h2[@class='post-title']/a/text()").extract_first()
					temp = post.xpath(".//img[@class='post-image']")
					meme["caption"] = temp.xpath("./@alt").extract_first().split(" " + meme["name"])[0]
					meme["image"] = temp.xpath("./@src-nsfw").extract_first() if temp.xpath("./@src-nsfw") else \
						temp.xpath("./@src").extract_first()
					meme["score"] = "".join(post.xpath(".//div[@class='sharecounts']/p//text()").re("\d+"))
					yield meme
				# else:
				# 	raise CloseSpider(reason="Previously crawled content found.")
		next_page = response.xpath("//a[@id='page-next']/@href")
		if next_page:
			url = response.urljoin(next_page.extract_first())
			yield scrapy.Request(url, self.parse)

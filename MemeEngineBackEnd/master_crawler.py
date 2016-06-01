from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from spiders.imgflip import ImgFlipSpider
from spiders.imgur import ImgUrSpider

# from spiders.memecenter import MemeCenterSpider
from spiders.memegenerator import MemeGeneratorSpider
from spiders.memestache import MemestacheSpider
from spiders.quickmeme import QuickMemeSpider

process = CrawlerProcess(get_project_settings())
process.crawl(ImgFlipSpider)
process.crawl(ImgUrSpider)
# process.crawl(MemeCenterSpider)
process.crawl(MemeGeneratorSpider)
process.crawl(MemestacheSpider)
process.crawl(QuickMemeSpider)
process.start()

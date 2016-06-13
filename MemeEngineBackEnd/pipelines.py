# coding=utf-8
import logging
import re

import pymongo
from nltk import PorterStemmer, download, RegexpTokenizer
from nltk.corpus import stopwords
from scrapy.exceptions import DropItem


class DuplicateCheckerPipeline(object):  # TODO Check for memes which contain similar text and captions as well
	def __init__(self, mongo_uri, mongo_db):
		self.mongo_uri = mongo_uri
		self.mongo_db = mongo_db

	@classmethod
	def from_crawler(cls, crawler):
		return cls(
			mongo_uri=crawler.settings.get("MONGODB_URI"),
			mongo_db=crawler.settings.get("MONGODB_DATABASE")
		)

	def open_spider(self, spider):
		self.client = pymongo.MongoClient(self.mongo_uri)
		self.db = self.client[self.mongo_db]
		source = spider.allowed_domains[0]
		self.seen = set(result["url"] for result in self.db.memes.find({"_id.source": source}, {"_id": 0, "url": 1}))

	def close_spider(self, spider):
		self.client.close()

	def process_item(self, meme, spider):
		if meme["url"] in self.seen:
			self.db.memes.update_one({"_id": {"source": meme["source"], "meme_id": meme["id"]}},
									 {"$set": {"score": meme["score"]}})
			raise DropItem("Duplicate meme found, updating db with latest information.")
		else:
			self.seen.add(meme["url"])
		return meme


class CleanserPipeline(object):
	def process_item(self, meme, spider):
		if meme["name"] is None:
			meme["name"] = ""
		if meme["title"] is None:
			meme["title"] = ""
		if meme["caption"] is None:
			meme["caption"] = ""
		if meme["score"] is None:
			meme["score"] = '0'
		return meme


class ValidatorPipeline(object):
	only_digits = re.compile("^-?\d+$")
	valid_url = re.compile("^((http[s]?|ftp):\/)?\/?([^:\/\s]+)((\/\w+)*\/)([\w\-\.]+[^#?\s]+)(.*)?(#[\w\-]+)?$")

	def process_item(self, meme, spider):
		if not re.match(self.only_digits, meme["score"]):
			raise DropItem("Incorrect SCORE format.")
		else:
			meme["score"] = int(meme["score"])
		if not re.match(self.valid_url, meme["url"]):
			raise DropItem("Incorrect URL format.")
		if not re.match(self.valid_url, meme["image"]):  # TODO Improve this filter
			raise DropItem("Incorrect IMAGE URL format.")
		if re.match(self.valid_url, meme["caption"]):
			raise DropItem("Possible spam in caption.")
		if re.match(self.valid_url, meme["title"]):
			raise DropItem("Possible spam in title.")
		return meme


class NormalizerPipeline(object):
	tokenizer = RegexpTokenizer("\w+")
	stemmer = PorterStemmer()

	def process_item(self, meme, spider):
		text = meme["name"] + " " + meme["title"] + " " + meme["caption"]
		tokens = None
		filtered = None
		while True:
			try:
				tokens = [self.stemmer.stem(token) for token in self.tokenizer.tokenize(text.lower())]
				filtered = set(tokens) - set(stopwords.words("english"))
			except LookupError:
				download("stopwords")
			else:
				break
		if not filtered:
			raise DropItem("No tokens found in meme")
		meme["postings"] = {key: tokens.count(key) for key in filtered}
		meme["length"] = reduce(lambda x, y: x + y, meme["postings"].itervalues())
		return meme


class DBInserterPipeline(object):
	def __init__(self, mongo_uri, mongo_db):
		self.mongo_uri = mongo_uri
		self.mongo_db = mongo_db

	@classmethod
	def from_crawler(cls, crawler):
		return cls(
			mongo_uri=crawler.settings.get("MONGODB_URI"),
			mongo_db=crawler.settings.get("MONGODB_DATABASE")
		)

	def open_spider(self, spider):
		self.client = pymongo.MongoClient(self.mongo_uri)
		self.db = self.client[self.mongo_db]

	def close_spider(self, spider):
		self.client.close()

	def process_item(self, meme, spider):
		self.add_to_database(meme)
		update_count = self.update_dictionary(meme)
		logging.log(logging.INFO, "Indexed meme %s -> %d dictionary entries updated." % (meme["url"], update_count))
		return meme

	def add_to_database(self, meme):
		self.db.memes.insert_one(
			{
				"_id": {"source": meme["source"], "meme_id": meme["id"]},
				"url": meme["url"],
				"image": meme["image"],
				"name": meme["name"],
				"title": meme["title"],
				"caption": meme["caption"],
				"score": meme["score"],
				"length": meme["length"],
				"postings": meme["postings"]
			})

	def update_dictionary(self, meme):
		bulk = self.db.dictionary.initialize_unordered_bulk_op()
		for term, freq in meme["postings"].iteritems():
			bulk.find({"_id": term}).upsert().update_one(
				{
					"$set": {"_id": term},
					"$inc": {"total_documents": 1, "total_frequency": freq}
				})
		execute = bulk.execute()
		return execute["nUpserted"] + execute["nModified"]

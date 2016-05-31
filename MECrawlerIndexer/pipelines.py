# coding=utf-8
import re

import pymongo
from nltk import PorterStemmer, download, RegexpTokenizer
from nltk.corpus import stopwords
from scrapy.exceptions import DropItem, CloseSpider


class DuplicateCheckerPipeline(object):
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
		client = pymongo.MongoClient(self.mongo_uri)
		db = client[self.mongo_db]
		self.seen = [result["url"] for result in db.Memes.find({}, {"url": 1})]
		if self.seen is None:
			self.seen = []
		client.close()

	def process_item(self, meme, spider):
		if meme["url"] in self.seen:
			raise CloseSpider("Duplicate meme found: %s" % meme)
		else:
			self.seen.append(meme["url"])
		return meme


class ValidatorPipeline(object):
	only_digits = re.compile("^-?\d+$")
	valid_url = re.compile("^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w+\.-]*)*\/?$")

	def process_item(self, meme, spider):
		if not re.match(self.only_digits, meme["score"]):
			raise DropItem("Incorrect SCORE format in %s" % meme)
		if not re.match(self.valid_url, meme["url"]):
			raise DropItem("Incorrect URL format in %s" % meme)
		if not re.match(self.valid_url, meme["image"]):
			raise DropItem("Incorrect IMAGE URL format in %s" % meme)
		if re.match(self.valid_url, meme["caption"]) or re.match(self.valid_url, meme["title"]):
			raise DropItem("Possible spam in %s" % meme)
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
		meme["postings"] = {key: tokens.count(key) for key in filtered}
		meme["length"] = reduce(lambda x, y: x + y, meme["postings"].itervalues())
		return meme


class DBInserterPipeline(object):
	global_postings = {}

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
		if self.global_postings:
			bulk = self.db.Dictionary.initialize_unordered_bulk_op()
			for term, freq in self.global_postings.iteritems():
				bulk.find({"_id": term}).upsert().update_one(
					{
						"$set": {"_id": term},
						"$inc": {"total_documents": freq[0], "total_frequency": freq[1]}
					})
			bulk.execute()
		self.client.close()

	def process_item(self, meme, spider):
		memes_id = {"source": meme["source"], "meme_id": meme["id"]}
		self.db.Memes.insert_one(
			{
				"_id": memes_id,
				"url": meme["url"],
				"image": meme["image"],
				"name": meme["name"],
				"title": meme["title"],
				"caption": meme["caption"],
				"score": meme["score"],
				"length": meme["length"]
			})
		self.db.Postings.insert_many(
			[{"_id": {"term": term, "Memes_id": memes_id}, "frequency": frequency}
			 for term, frequency in meme["postings"].iteritems()], False)

		for term, frequency in meme["postings"].iteritems():
			global_frequency = self.global_postings.get(term)
			if global_frequency is not None:
				global_frequency[0] += 1
				global_frequency[1] += frequency
			else:
				global_frequency = [1, frequency]
			self.global_postings[term] = global_frequency
		return meme

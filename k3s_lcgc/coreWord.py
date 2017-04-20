from .dbModel import DbModel
from nltk import word_tokenize
from nltk import pos_tag
from .utility import Utility
import sys
from nltk.stem.porter import PorterStemmer
from .nlp import NLP
import math
from nltk.corpus import stopwords
from nltk.corpus import stopwords



class CoreWord(DbModel):


	def __init__(self, identifier):
		DbModel.__init__(self, identifier)
		self.tableName = 'core_word'
		self.primaryKey = 'core_wordid'
		self.fields = ['core_wordid', 'stemmed_word', 'word', 'pos_type', 'number_of_blocks', 'count']
		self.ignoreExists = ['number_of_blocks']
		self.stemmer = PorterStemmer()
		self.nlpProcessor = NLP()
		return


	def save(self, data):
		itemid = None
		item = self.read(data)

		if not item:
			data['number_of_blocks'] = 1
			itemid = self.insert(data)
		else:
			itemid = item[0][0]
			if item[0][3] and (data['pos_type'] != item[0][3]):
				data['pos_type'] = item[0][3] + ',' + data['pos_type']
			data['number_of_blocks'] = int(item[0][5]) + 1
			self.update(data, itemid)
				
		return itemid


	"""
	ADJ	adjective
	ADP	adposition
	ADV	adverb
	CONJ conjunction
	DET	determiner
	NOUN noun
	NUM	numeral	
	PRT	particle
	PRON pronoun
	VERB verb
	"""
	def saveWords(self, textBlock):
		actualWords = self.getWords(textBlock, False)
		words = self.getWords(textBlock, True)				

		totals = {}
		for word in actualWords:
			stemmedWord = self.stemmer.stem(word)
			if stemmedWord in totals.keys():
				totals[stemmedWord] += 1
			else:
				totals[stemmedWord] = 1

		
		if len(totals):
			for word in words:
				if word[0] == word[1]:
					# Puncuation
					continue

				data = {}
				data['pos_type'] = word[1]
				data['word'] = word[0]
				data['stemmed_word'] = self.stemmer.stem(word[0])
				
				keys = totals.keys()
				if data['stemmed_word'] in keys:
					data['count'] = totals[data['stemmed_word']]
				elif word in keys:
					data['count'] = totals[word]
				else:
					data['count'] = 1
				
				if (word in stopwords.words('english')) or (data['stemmed_word'] in stopwords.words('english')):
					data['stop_word'] = 1
				else:
					data['stop_word'] = 0

				self.save(data)

		return words


	def getWords(self, textBlock, tagPartsOfSpeach = False):
		words = word_tokenize(textBlock)
		if not tagPartsOfSpeach:
			return words
		return pos_tag(words)


	def markStopWords(self):
		sql = ("UPDATE core_word SET stop_word = 1 WHERE pos_type NOT LIKE '%NN%'")
		self.mysql.updateOrDelete(sql, [])
		return 


 




import sys
import re
import os
from .directory import Directory
from .file import File
from .nlp import NLP
from .utility import Utility
from .topology import Topology
from .coreWord import CoreWord
from .word import Word
from .localContext import LocalContext
from .textNode import TextNode
from .wordContext import WordContext
from .wordCloud import WordCloud
from .textNodeCloud import TextNodeCloud



class TopologyProcessor():


	def __init__(self, sourceIdentifier, sourcePath):
		self.log = Log()
		self.mainPath = File.join(self.config.DATA_PATH, sourceIdentifier)
		self.processedPath = File.join(self.mainPath, 'processed')
		self.localContextImagesPath = File.join(self.mainPath, 'local-context')
		self.sourceIdentifier = sourceIdentifier
		return


	def topologySetUp(self):
		topologyBuilder = Topology(self.sourceIdentifier)
		topologyBuilder.setUp()
		return

	def saveBlocksInMysql(self, limit = None, processCore = True):
		topologyBuilder = Topology(self.sourceIdentifier)

		sourceDir = Directory(self.processedPath)
		files = sourceDir.scan()

		if not files:
			return

		files.sort()
		index = 0

		for fileName in files:
			if fileName[0] == '.':
				continue
			filePath = File.join(self.processedPath, fileName)
			file = File(filePath)
			data = {}
			data['source_identifier'] = file.getFileName()
			data['text_block'] = file.read()
			data['text_block'] = re.sub('\'s', '', str(data['text_block']))
			data['text_block'] = re.sub('(-?)\n', '', str(data['text_block']))
			data['text_block'] = re.sub('/|\|', ' ', str(data['text_block']))
			data['text_block'] = re.sub('\'|"|\(|\)|\{|\}|[|\]|<[a-zA-Z0-9\"\'-_\s"]+>', '', str(data['text_block']))
			data['text_block'] = re.sub('\s+', ' ', str(data['text_block']))
			data['text_block'].encode("utf-8")
			topologyBuilder.addTextNode(data, processCore)

			index += 1
			if (index == limit):
				break;

		
		return

	def calculateTfIdf(self):
		wordProcessor = Word(self.sourceIdentifier)
		wordProcessor.calculateTfIdf()
		return


	def calculateLocalContextImportance(self):
		wordProcessor = Word(self.sourceIdentifier)
		wordProcessor.calculateLocalContextImportance()
		return


	def buildWordContext(self):
		return;


	def buildCloud(self, savePoints = False):
		wordCloud = WordCloud(self.sourceIdentifier)
		if(savePoints):
			wordCloud.savePoints()

		wordCloud1 = WordCloud(self.sourceIdentifier)
		wordCloud1.generateLCCsv()
		return


	def buildGlobalWord(self):
		wordCloud = WordCloud(self.sourceIdentifier)
		wordCloud.wordCloudMatPlotLib()
		return


	def buildGlobalText(self):
		cloud = TextNodeCloud(self.sourceIdentifier)
		cloud.textCloudMatPlotLib()
		return


	def buildTextCloud(self, savePoints = False):
		cloud = TextNodeCloud(self.sourceIdentifier)
		if(savePoints):
			cloud.savePoints()
		cloud1 = TextNodeCloud(self.sourceIdentifier)
		cloud1.generateCsv()
		return

	'''
	def buildTextNodeCloud(self, nodeid):
		wordCloud = WordCloud(self.sourceIdentifier)
		wordCloud.buildTextNodeCloud(nodeid)
		return
	'''

	def stopWordsUpdate(self):
		coreWprdProcessor = CoreWord(self.sourceIdentifier)
		coreWprdProcessor.markStopWords()
		return


	def calculateWordZone(self):
		wordProcessor = Word(self.sourceIdentifier)
		wordProcessor.calculateZone()
		return


	def generateLocalContextImages(self, limit = None):
		textNodeProcessor = TextNode(self.sourceIdentifier)

		index = 0
		filterLowerRatedNouns = 0
		for textBlock in textNodeProcessor.getAllByBatch():
			if index == limit:
				break;

			textBlockText = re.sub('file:.+M\]', '', textBlock[2])
				
			lc = LocalContext(textBlockText, self.sourceIdentifier, 0.2)
			lc.reflectRepresentatives(textBlock[1], filterLowerRatedNouns)
			index += 1
			if index == limit:
				break

		return






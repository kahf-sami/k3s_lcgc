from .dbModel import DbModel
from .edge import Edge
from .word import Word
from .context import Context
from .nlp import NLP
import sys
import re
from .utility import Utility
import math
from .localContext import LocalContext
from .coreWord import CoreWord
import ast
from .config import Config
from .file import File
from .localContextReflector import LocalContextReflector
from .wordCloud import WordCloud

class TextNodeCloud(DbModel):


	def __init__(self, identifier):
		DbModel.__init__(self, identifier)
		self.config = Config()
		self.identifier = identifier
		self.tableName = 'text_point'
		self.primaryKey = 'text_pointid'
		self.fields = ['text_pointid', 'nodeid', 'label', 'x', 'y', 'r', 'theta']
		self.ignoreExists = ['theta', 'r', 'x', 'y', 'label']
		self.wordProcessor = Word(identifier)
		self.mainPath = File.join(self.config.ROOT_PATH, 'Web', self.identifier + '_text_node.csv')
		self.maxPoints = 3
		return



	def getRepresentativesByBatch(self):
		sql = "SELECT nodeid, representatives FROM text_node"
		return self.mysql.query(sql, [], True)



	def savePoints(self):
		self.mysql.truncate(self.tableName)
		cursor = self.getRepresentativesByBatch()

		for representative in cursor:
			representativeList = ast.literal_eval(re.sub('\'', '"', str(representative[1])))
			self.calculateAndSavePoint(representativeList, representative[0])

		return


	def calculateAndSavePoint(self, representativeList, nodeid):
		if not representativeList:
			return None

		details = self.getRepresentativesDetails(nodeid, representativeList)
		
		numberOfWords = 0
		sumX = 0
		sumY = 0
		label = str(nodeid) + ': '
		divider = ''

		for word in details:
			#print(word)
			#if numberOfWords <= self.maxPoints:
			sumX += word[3]
			sumY += word[4]
			numberOfWords += 1
			
			label += divider + word[0]
			divider = ', '
			#print(sumX)
			#print(sumY)
			#print('------------------')

		#print(numberOfWords)

		data = {}
		data['nodeid'] = nodeid
		data['label'] = label
		if numberOfWords:
			data['y'] = sumY / numberOfWords
			data['x'] = sumX / numberOfWords
			data['r'] = math.sqrt(float(data['x']) * float(data['x']) + float(data['y']) * float(data['y']))
		else:
			return

		print(data)
		print('--------------')
		#sys.exit()
		self.save(data);
		return


	def generateCsv(self, representatives = None, filePath = None):
		cursor = self.getPointsByBatch()

		if filePath:
			file = File(filePath)
		else:
			file = File(self.mainPath)
		file.remove()

		for word in cursor:
			#print(word)
			if len(word[1]) < 2:
				continue

			data = {}
			data['nodeid'] = word[0]
			data['label'] = word[1]
			data['x'] = word[2]
			data['y'] = word[3]
			data['r'] = word[4]
			
			file.write(data)

		return

	def textCloudMatPlotLib(self):
		'''		
		wordCloud = WordCloud(self.identifier)
		results = wordCloud.getWordNodes()

		nodes = results[0]
		x = results[3] 
		y =  results[4]
		sizes = results[5] 
		colors = results[6]
		currentColors = results[7]
		'''
		cursor = self.getPointsByBatch()
		
		nodes = {}
		x = []
		y = []
		sizes = []
		colors = []
		
		theta = 360
		maxR = None
		minR = None
		polygonNodes = {}

		nodeIndex = 0
		for batch in cursor:
			node = {}
			node['index'] = nodeIndex
			node['label'] = re.sub('.txt', '', str(batch[5]))
			#node['label'] = str(batch[5]) + ': ' + str(batch[1])
			node['color'] = 'red'
			node['size'] = 10
			node['x'] = batch[2]
			node['y'] = batch[3]
			node['r'] = batch[4]
			
			x.append(node['x'])
			y.append(node['y'])
			colors.append(node['color'])
			sizes.append(node['size'])

			nodes[batch[0]] = node
			polygonNodes[batch[0]] = node

			if not minR or minR > node['r']:
				minR = node['r']

			if not maxR or maxR < node['r']:
				maxR = node['r']

			nodeIndex += 1

		distance = maxR * 0.4

		lcr = LocalContextReflector(self.identifier)
		polygons = None
		#polygons = lcr.getPolygons(polygonNodes, distance)
		'''
		results = wordCloud.addCurrentColorLegend(nodes, nodeIndex, maxR, currentColors, x, y, colors, sizes)
		nodes = results[0]
		x = results[1]
		y = results[2]
		colors = results[3]
		sizes = results[4]
		'''
		lcr.create(x, y, colors, nodes, sizes, 'text-global', polygons)

		return

			
	def getPointsByBatch(self):
		sql = ("SELECT text_point.nodeid, label, x, y, r, source_identifier "
			"FROM text_point "
			"JOIN text_node ON text_node.nodeid = text_point.nodeid WHERE text_point.nodeid != 10")
		return self.mysql.query(sql, [], True)	


	def getWordDetails(self, word):
		sql = ("SELECT number_of_blocks, local_avg "
			"FROM word "
			"WHERE word.stemmed_word = %s")
		
		return self.mysql.query(sql, [word])


	def getRepresentativesDetails(self, nodeid, representativeList):
		sql = ("select word.word, weight, zone, x, y "
			"from local_context "
			"join word on local_context.word = word.stemmed_word "
			"join word_point on word.wordid = word_point.wordid "
			"where local_context.nodeid = %s "
			"and local_context.word in ( ")

		params = []
		params.append(nodeid)
		divider = ''
		for word in representativeList:
			sql += divider + '%s'
			divider = ', '
			params.append(word)

		sql += ") and number_of_blocks > 1 order by zone desc, weight desc"

		return self.mysql.query(sql, params)



from .dbModel import DbModel
from .utility import Utility
from .config import Config
from .file import File
from .utility import Utility
import sys
import math
from .word import Word
import ast
import re
import numpy
from .localContextReflector import LocalContextReflector


class WordCloud(DbModel):


	def __init__(self, identifier):
		DbModel.__init__(self, identifier)
		self.config = Config()
		self.identifier = identifier
		self.tableName = 'word_point'
		self.primaryKey = 'word_pointid'
		self.fields = ['word_pointid', 'wordid', 'label', 'x', 'y', 'r', 'theta']
		self.maxX = self.maxNumberOfSimilarBlocks()
		self.mainPath = File.join(self.config.ROOT_PATH, 'Web', self.identifier + '_all.csv')
		self.radius = self.calculateRadius()
		self.thetaIncrementPerZone = {}		
		self.radiusIncrementFactor = 10
		self.thetaIncrementFactorPerZone = {}
		self.loadThetaIncrementFactor()
		print(self.mainPath)
		self.zoneColors = ['crimson', 'fuchsia', 'pink', 'plum', 
			'violet', 'darkorchid', 'lavender', 'royalblue', 
			'dodgerblue', 'lightskyblue', 'aqua', 'aquamarine', 'green', 
			'lime', 'yellowgreen', 'yellow', 'lightyellow', 'lightsalmon', 
			'coral', 'tomato', 'brown', 'maroon']

		return


	def calculateRadius(self):
		totalTextNodes = self.getTotalTextNodes();
		if not totalTextNodes:
			return 0

		# The radius of a circle is number of nodes
		radius = math.ceil(totalTextNodes * 7 / 44)
		return radius


	def savePoints(self):
		totalTextNodes = self.getTotalTextNodes();

		self.mysql.truncate(self.tableName)
		cursor = self.getWordsByBatch()

		for word in cursor:
			self.calculateAndSavePoint(word, totalTextNodes)

		return


	def calculateAndSavePoint(self, word, totalTextNodes):
		wordProcessor = Word(self.identifier)
		#localContextImportance = wordProcessor.localContextImportance(word[1])

		zone =  word[8]
		if not zone in self.thetaIncrementPerZone.keys():
			self.thetaIncrementPerZone[zone] = 0
		else:
			self.thetaIncrementPerZone[zone] += self.thetaIncrementFactorPerZone[zone]

		data = {}
		data['wordid'] = word[0]
		data['label'] = word[1]
		#data['r'] = word[5] #tf-idf
		data['r'] = self.radiusIncrementFactor * zone
		data['theta'] = self.thetaIncrementPerZone[zone]
		data['x'] = data['r'] * numpy.cos(numpy.deg2rad(data['theta']))
		data['y'] = data['r'] * numpy.sin(numpy.deg2rad(data['theta']))

		self.save(data);


	def getWordsByBatch(self):
		sql = ("SELECT wordid, word, stemmed_word, count, number_of_blocks, tf_idf, local_avg, signature, zone "
			"FROM word ORDER BY zone, wordid")
		
		return self.mysql.query(sql, [], True)



	def getPoint(self, word):
		sql = "SELECT word_pointid FROM word_point WHERE label = %s"

		params = []
		params.append(word);
		return self.mysql.query(sql, params)


	def maxNumberOfSimilarBlocks(self):
		sql = ("SELECT MAX(number_of_blocks) FROM word ")
		result = self.mysql.query(sql, [])
		return result[0][0]


	def generateLCCsv(self, representatives = None, filePath = None):
		cursor = self.getPointsByBatch()

		if filePath:
			file = File(filePath)
		else:
			file = File(self.mainPath)
		file.remove()

		nodes = {}

		for batch in cursor:
			words = [item for item in cursor.fetchall()]
			for word in words:
				if len(word[1]) < 2 or word[4] == 1 or word[8] > 18:
					continue

				data = {}
				data['word'] = word[1]
				data['local_avg'] = word[6]
				data['global_docs'] = word[4]
				data['global_tf_idf'] = math.ceil(word[5])
				data['global_cluster'] = 'zone' + str(word[8])
				data['global_local'] = 2 * float(data['global_tf_idf'])  + 0.1 * float(data['local_avg'])
				data['signature'] = word[7]
				data['x'] = word[9]
				data['y'] = word[10]
				data['r'] = word[11]
				data['theta'] = word[12]

				if representatives and (word[1] in representatives):
					data['global_cluster'] = 2

				#print(word)
				#self.getRelatedWords(word[0])
				
				file.write(data)


	def wordCloudMatPlotLib(self, representatives = None, filePath = None):
		results = self.getWordNodes()

		nodes = results[0]
		maxR = results[2]
		x = results[3] 
		y =  results[4]
		sizes = results[5] 
		colors = results[6]
		currentColors = results[7]

		distance = maxR * 0.4
		lcr = LocalContextReflector(self.identifier)
		polygons = None
		#polygons = lcr.getPolygons(nodes, distance)
		'''
		results = self.addCurrentColorLegend(nodes, len(nodes), maxR, currentColors, x, y, colors, sizes)
		nodes = results[0]
		x = results[1]
		y = results[2]
		colors = results[3]
		sizes = results[4]		
		'''
		lcr.create(x, y, colors, nodes, sizes, 'word-global', polygons)
		return


	def getWordNodes(self):
		cursor = self.getPointsByBatch()

		nodes = {}
		x = []
		y = []
		sizes = []
		colors = []
		theta = 360
		maxR = 0
		minR = None
		currentColors = {}

		nodeIndex = 0
		for batch in cursor:
			words = [item for item in cursor.fetchall()]
			for word in words:
				if len(word[1]) < 2 or word[4] == 1 or word[8] > 18 or len(word[1]) > 25:
					continue

				node = {}
				node['index'] = nodeIndex
				node['label'] = word[1]
				node['color'] = self.zoneColors[word[8]]
				node['size'] = math.ceil(word[6] * 5 / 1000) #Based on local context
				node['x'] = word[9]
				node['y'] = word[10]
				node['r'] = word[11]

				x.append(node['x'])
				y.append(node['y'])
				colors.append(node['color'])
				sizes.append(node['size'])

				nodes[word[1]] = node

				currentColors[word[8]] = self.zoneColors[word[8]]

				if not minR or minR > node['r']:
					minR = node['r']

				if not maxR or maxR < node['r']:
					maxR = node['r']

				nodeIndex += 1

		

		return [nodes, minR, maxR, x, y, sizes, colors, currentColors]


	def addCurrentColorLegend(self, nodes, nodeIndex, maxRadius, currentColors, x, y, colors, sizes):
		Y = 400

		if len(currentColors):
			for zone in range(1, 20):
				if zone not in currentColors.keys():
					continue
				node = {}
				node['index'] = nodeIndex
				node['label'] = 'zone - ' + str(zone)
				node['color'] = currentColors[zone]
				node['r'] = 0
				node['theta'] = 0
				node['zone'] = zone
				node['x'] = maxRadius - 15
				node['y'] = Y

				nodes[zone] = node 

				x.append(node['x'])
				y.append(node['y'])
				colors.append(node['color'])
				sizes.append(10)
				Y -= 20
				nodeIndex += 1

		return [nodes, x, y, colors, sizes]

			


	def buildTextNodeCloud(self, nodeid):
		representatives = self.getNodeRepresentative(nodeid)

		if not representatives:
			return

		pointsPath = File.join(self.config.ROOT_PATH, 'Web', self.identifier + '_' + str(nodeid) + '.csv')

		self.generateLCCsv(representatives, pointsPath)
		return

	
	def loadThetaIncrementFactor(self):
		self.thetaIncrementFactorPerZone = {}

		zones = self.getZones()

		if not zones:
			return

		for zone in zones:
			if zone[0] == 0:
				self.thetaIncrementFactorPerZone[zone[1]] = 0
			else:
				self.thetaIncrementFactorPerZone[zone[1]] = 360 / zone[0]
		return



	def getWordDetails(self, word):
		sql = ("SELECT wordid, word, stemmed_word, count, number_of_blocks, tf_idf, local_avg, signature "
			"FROM word "
			"WHERE word.word = %s")
		
		return self.mysql.query(sql, [word])



	def getNodeRepresentative(self, nodeid):
		sql = ("SELECT representatives "
			"FROM text_node "
			"WHERE nodeid = %s")
		result = self.mysql.query(sql, [nodeid])

		if result[0][0]:
			return ast.literal_eval(re.sub('\'', '"', str(result[0][0])))

		return None


	def getPointsByBatch(self):
		sql = ("SELECT word.wordid, word.word, stemmed_word, count, number_of_blocks, tf_idf, local_avg, signature, zone, x, y, r, theta "
			"FROM word "
			"JOIN word_point ON word.wordid=word_point.wordid "
			"ORDER BY zone, wordid")
		
		return self.mysql.query(sql, [], True)

		sql = ("SELECT label, y as local_avg_weight, x as global_docs, tf_idf "
			"FROM word "
			"JOIN word_point ON word_point.wordid = word.wordid ")
		return self.mysql.query(sql, [], True)


	def getTotalWords(self):
		sql = ("SELECT count(*) "
			"FROM wordQA ")
		result = self.mysql.query(sql, [])
		return result[0][0]


	def getTotalTextNodes(self):
		sql = ("SELECT count(*) "
			"FROM text_node ")
		result = self.mysql.query(sql, [])
		return result[0][0]


	def getZones(self):
		sql = ("SELECT count(wordid), zone "
			"FROM word "
			"GROUP BY zone")
		result = self.mysql.query(sql, [])
		
		return result

				





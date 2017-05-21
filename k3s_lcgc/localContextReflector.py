from .file import File
from .directory import Directory
from .config import Config
import numpy as np
import matplotlib.pyplot as plot
from matplotlib.path import Path
import matplotlib.patches as patches
import matplotlib.cm as cmx
import matplotlib.colors as colors
from nltk import word_tokenize
import sys
import math


class LocalContextReflector():


	def __init__(self, identifier):
		self.config = Config()
		self.identifier = identifier
		self.path = File.join(self.config.DATA_PATH, self.identifier, 'local-context-reflector')

		directory = Directory(self.path)
		directory.create()
		return


	def create(self, x, y, colors, nodes, pointSizes = 5, fileName = None, edges = None):
		plot.cla() # Clear the figure

		self.figure = plot.figure(figsize=(200, 200))
		self.axis = self.figure.add_subplot(111)
		self.axis.grid(color='white', linestyle='solid')
		graph = self.axis.scatter(x, y, c = colors, marker='o', s=pointSizes, edgecolors = colors)
		
		for node in nodes:
			if nodes[node]['x'] < 0:
				horizontalalignment = 'right'
			else:
				horizontalalignment = 'left'
			if nodes[node]['y'] < 0:
				verticalalignment = 'down'
			else:
				verticalalignment = 'top'
			
			self.axis.annotate(nodes[node]['label'], (nodes[node]['x'], nodes[node]['y']), color='black', horizontalalignment=horizontalalignment, verticalalignment=verticalalignment, fontsize=12)
		

		if edges:
			for edge in edges:
				#print(edge)
				plot.plot([edges[edge]['start-x'], edges[edge]['end-x']], [edges[edge]['start-y'], edges[edge]['end-y']], lw=2, c = 'gray')


		'''
		if contextPolygons:
			index = 0
			for polygon in contextPolygons:
				totalPoints = len(polygon)
				firstPoint = True
				codes = []
				
				if totalPoints == 1:
					continue

				for point in polygon:
					if firstPoint:
						codes.append(Path.MOVETO)
						firstPoint = False
					elif polygon == totalPoints - 1:
						#lastPoint
						codes.append(Path.CLOSEPOLY)
						firstPoint = True
					else:
						codes.append(Path.LINETO)

				path = Path(polygon, codes)
				patch = patches.PathPatch(path, color=black, alpha=0.2)
				self.axis.add_patch(patch)
				index += 1
		
		'''		

		plot.show()

		self.figure.savefig(File.join(self.path, fileName + '.png'))
		return


	def getPolygons(self, nodes, distance):
		if not nodes:
			return None


		edges = {}	

		for node1 in nodes:
			node1 = nodes[node1]
			
			for node2 in nodes:
				node2 = nodes[node2]

				if node1['index'] == node2['index']:
					continue

				xDistance = node2['x'] - node1['x']
				yDistance = node2['y'] - node1['y']
				distanceBetweenNodes = math.sqrt(xDistance * xDistance + yDistance * yDistance)

				if distanceBetweenNodes > distance:
					continue

				identifier = str(node2['index']) + '-' + str(node1['index'])
				if identifier in edges.keys():
					continue

				edges[identifier] = {'start-x' : node1['x'], 'start-y' : node1['y'], 'start-w' : node1['label'], 'end-x' : node2['x'], 'end-y' : node2['y'], 'end-w' : node2['label']}
				#print(node1)
				#print(node2)
				#print(distanceBetweenNodes)
				#print(edges[identifier])
				


		#print(edges)
		#print(len(edges))
		#print(len(nodes))
		#print(distance)
		return edges




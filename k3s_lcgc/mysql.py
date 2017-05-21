from __future__ import print_function
import mysql.connector as connector
from mysql.connector import errorcode
from datetime import date, datetime, timedelta
import sys

class MySql():


	def __init__(self, config):
		self.config = config
		self.connection = None
		self.batchConnection = None
		self.cursor = None
		self.batchCursor = None
		return


	def createDb(self, name):
		database = connector.connect(user = self.config['userName'], password = self.config['password'], host = self.config['host'])
		cursor = database.cursor()
		try:
			cursor.execute('CREATE DATABASE IF NOT EXISTS ' + name)
		except connector.Error as err:
			print("Failed creating database: {}".format(err))
		return


	def dropDb(self, name):
		database = connector.connect(user = self.config['userName'], password = self.config['password'], host = self.config['host'])
		cursor = database.cursor()
		try:
			cursor.execute('DROP DATABASE IF  EXISTS ' + name)
		except connector.Error as err:
			print("Failed drop database: {}".format(err))
		return


	def connect(self):
		self.connection = connector.connect(user = self.config['userName'], password = self.config['password'], host = self.config['host'], database=self.config['name'])
		self.cursor = self.connection.cursor()
		self.batchConnection = connector.connect(user = self.config['userName'], password = self.config['password'], host = self.config['host'], database=self.config['name'])
		self.batchCursor =  self.batchConnection.cursor()
		return


	def createTables(self, tables):
		if self.cursor == None:
			self.connect()

		for name in tables:
			try:
				self.cursor.execute(tables[name])
			except connector.Error as err:
				if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
					print("already exists.")
				else:
					print(err.msg)

		return

	def dropTables(self, tables):
		if self.cursor == None:
			self.connect()

		for name in tables:
			try:
				self.cursor.execute('DROP TABLE IF EXISTS ' + name)
			except connector.Error as err:
				print(err.msg)

		return


	def query(self, sql, data = [], batch = None):
		if self.cursor == None:
			self.connect()
		
		
		
		if batch:
			self.batchCursor.execute(sql, data)
			return self.batchCursor

		self.cursor.execute(sql, data)
		results = [item for item in self.cursor.fetchall()]
		return results


	def insert(self, sql, data):
		if self.cursor == None:
			self.connect()
		
		self.cursor.execute(sql, data)
		self.connection.commit()

		return self.cursor.lastrowid


	def updateOrDelete(self, sql, data = []):
		if self.cursor == None:
			self.connect()
		
		self.cursor.execute(sql, data)
		self.connection.commit()

		return


	def close(self):
		self.cursor.close()
		self.connection.close()
		return


	def truncate(self, tableName):
		self.updateOrDelete('TRUNCATE ' + tableName, [])
		return







from .config import Config
from .mysql import MySql
from .textNode import TextNode
from .context import Context 
from .word import Word 

class Topology():


	def __init__(self, identifier):
		self.identifier = identifier
		self.dbConfig = Config.getDbUserConfig()
		self.dbConfig['name'] = identifier
		self.mysql = MySql(self.dbConfig)
		return


	def setUp(self):
		self.mysql.createDb(self.identifier)
		self.mysql.createTables(self.getTables())
		return


	def addTextNode(self, data, processCore):
		textNode = TextNode(self.identifier)
		return textNode.save(data, processCore)


	def extractContext(self):
		context = Context(self.identifier)
		context.buildBasic()
		return


	def assignWordEdges(self):
		wordProcessor = Word(self.identifier)
		wordProcessor.addEdges()
		return


	def getTables(self):
		tables = {}
		
		tables['text_node'] = (
			"CREATE TABLE IF NOT EXISTS text_node ("
			"nodeid INT(11) NOT NULL AUTO_INCREMENT,"
			"source_identifier VARCHAR (255) NOT NULL DEFAULT '',"
			"text_block LONGTEXT,"
			"representatives LONGTEXT,"
			"dna VARCHAR(64) DEFAULT NULL,"
			"processed TINYINT(1) DEFAULT 0,"
			"PRIMARY KEY (nodeid)"
			") ENGINE=InnoDB DEFAULT CHARACTER SET=utf8")

		tables['core_word'] = (
			"CREATE TABLE IF NOT EXISTS core_word ("
			"core_wordid INT(11) NOT NULL AUTO_INCREMENT,"
			"word VARCHAR(255) NOT NULL,"
			"stemmed_word VARCHAR(255) NOT NULL,"
			"pos_type VARCHAR(255) NOT NULL,"
			"count INT(11) NOT NULL DEFAULT 0,"
			"number_of_blocks INT(11) NOT NULL DEFAULT 0,"
			"stop_word TINYINT(1) NOT NULL DEFAULT 0,"
			"PRIMARY KEY (core_wordid)"
			") ENGINE=InnoDB DEFAULT CHARACTER SET=utf8")

		tables['local_context'] = (
			"CREATE TABLE IF NOT EXISTS local_context ("
			"local_contextid INT(11) NOT NULL AUTO_INCREMENT,"
			"nodeid INT(11) NOT NULL,"
			"word VARCHAR(255) DEFAULT NULL,"
			"weight DOUBLE(11, 2) NOT NULL DEFAULT 0,"
			"PRIMARY KEY (local_contextid)"
			") ENGINE=InnoDB DEFAULT CHARACTER SET=utf8")

		tables['word'] = (
			"CREATE TABLE IF NOT EXISTS word ("
			"wordid INT(11) NOT NULL AUTO_INCREMENT,"
			"word VARCHAR(255) NOT NULL,"
			"stemmed_word VARCHAR(255) NOT NULL,"
			"count INT(11) NOT NULL DEFAULT 0,"
			"number_of_blocks INT(11) NOT NULL DEFAULT 0,"
			"tf_idf DOUBLE(11, 2) DEFAULT 0,"
			"signature INT(64) DEFAULT 0,"
			"local_avg DECIMAL(20,2) DEFAULT 0.00,"
			"zone TINYINT(1) DEFAULT 0,"
			"PRIMARY KEY (wordid)"
			") ENGINE=InnoDB DEFAULT CHARACTER SET=utf8")


		tables['context'] = (
			"CREATE TABLE IF NOT EXISTS context ("
			"contextid INT(11) NOT NULL AUTO_INCREMENT,"
			"parent_contextid INT(11) DEFAULT NULL,"
			"ancestor_contextid INT(11) DEFAULT NULL,"
			"name VARCHAR(255) NOT NULL,"
			"words LONGTEXT NOT NULL,"
			"weight DOUBLE(11, 2) NOT NULL DEFAULT 0,"
			"signature INT(64) NOT NULL DEFAULT 0,"
			"PRIMARY KEY (contextid)"
			") ENGINE=InnoDB DEFAULT CHARACTER SET=utf8")

		tables['edge'] = (
			"CREATE TABLE IF NOT EXISTS edge ("
			"edgeid INT(11) NOT NULL AUTO_INCREMENT,"
			"source_nodeid INT(11) NOT NULL,"
			"destination_nodeid INT(11) NOT NULL,"
			"weight DOUBLE(11, 2) NOT NULL DEFAULT 0,"
			"PRIMARY KEY (edgeid)"
			") ENGINE=InnoDB DEFAULT CHARACTER SET=utf8")

		
		tables['word_edge'] = (
			"CREATE TABLE IF NOT EXISTS word_edge ("
			"word_edgeid INT(11) NOT NULL AUTO_INCREMENT,"
			"source_wordid INT(11) NOT NULL,"
			"destination_wordid INT(11) NOT NULL,"
			"weight DOUBLE(11, 2) NOT NULL DEFAULT 0,"
			"PRIMARY KEY (word_edgeid)"
			") ENGINE=InnoDB DEFAULT CHARACTER SET=utf8")

		tables['word_cloud'] = (
			"CREATE TABLE IF NOT EXISTS word_point ("
			"word_pointid INT(11) NOT NULL AUTO_INCREMENT,"
			"wordid INT(11) NOT NULL,"
			"label VARCHAR (255) NOT NULL DEFAULT '',"
			"x DOUBLE(11, 2) DEFAULT 0,"
			"y DOUBLE(11, 2) DEFAULT 0,"
			"r DOUBLE(11, 2) DEFAULT 0,"
			"theta DOUBLE(11, 2) DEFAULT 0,"
			"PRIMARY KEY (word_pointid)"
			") ENGINE=InnoDB DEFAULT CHARACTER SET=utf8")

		tables['text_cloud'] = (
			"CREATE TABLE IF NOT EXISTS text_point ("
			"text_pointid INT(11) NOT NULL AUTO_INCREMENT,"
			"nodeid INT(11) NOT NULL,"
			"label TEXT NOT NULL,"
			"x DOUBLE(11, 2) DEFAULT 0,"
			"y DOUBLE(11, 2) DEFAULT 0,"
			"r DOUBLE(11, 2) DEFAULT 0,"
			"theta int(11) DEFAULT 0,"
			"PRIMARY KEY (text_pointid)"
			") ENGINE=InnoDB DEFAULT CHARACTER SET=utf8")
		
		return tables



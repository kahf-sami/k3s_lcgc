import K3S-LCGC


identifier = 'bhot'

self.ROOT_PATH = os.path.abspath(__file__ + "/../../")
		self.LIBRARY_PATH = os.path.join(self.ROOT_PATH, 'K3S')
		self.DATA_PATH = os.path.join(self.ROOT_PATH, 'data')
		self.DATA_PROCESSED_PATH = os.path.join(self.DATA_PATH, 'processed')
		self.LOG_LOCATION = os.path.join(self.ROOT_PATH, 'temp', 'logs')
		self.RUN_LOCATION = os.path.join(self.ROOT_PATH, 'temp', 'runs')


	@staticmethod
	def getDbUserConfig():
		return {'userName': 'k3s_user', 'host':'localhost', 'password': 'b15m1llah'}

#fileProcessor = K3S.Processor(identifier)
#fileProcessor.clean()
#fileProcessor.createSourceSetup()
#fileProcessor.copy('/home/ishrat/research/K3S/data/stephen_hawking_a_brief_history_of_time.pdf')
#fileProcessor.extractBlocks()


processor = K3S.TopologyProcessor(identifier)
#processor.topologySetUp()
#processor.saveBlocksInMysql(None, True)
#processor.calculateTfIdf()
#processor.stopWordsUpdate()
#processor.calculateWordZone()
#processor.calculateLocalContextImportance()
#processor.buildCloud(True)

#processor.buildTextCloud(True)
#processor.generateLocalContextImages(1)
#processor.buildGlobalWord()
processor.buildGlobalText()
import GW
import types
import sys


class GWApp:
	def __init__(self,g):
		self.graph = g
		graph = self.graph
		graph.startTransaction(GW.XRO)

		result = []
		q = """FROM {'#role-topic'} DO DONE AS INDEXES"""	
		res = graph.STMQLExec(q)
		assert(len(res) == 1)

		self.topicRoleIndex = res[0]

		result = []
		q = """FROM {'#at-topic-occurrence'} DO DONE AS INDEXES"""	
		res = graph.STMQLExec(q)
		assert(len(res) == 1)

		self.atTopicOccurrenceIndex = res[0]

	# convenience constructor for TMObject
	def TMObject(self,arg):
		return self.TMObject_constructor(arg,self)

	def isTopicRoleIndex(self,index):
		return index == self.topicRoleIndex


	def end(self):
		self.graph.commitTransaction()


	def getTopicWithID(self,id):
		graph = self.graph		
		res = []
		q = """FROM {'%s'} DO DONE AS INDEXES""" % id
		res = graph.STMQLExec(q)
		if len(res) > 0:
			return self.TMObject(res[0])
		else:
			return None
		

	def getAllWhereBaseNameIs(self,basename):
		graph = self.graph
		result = []
		q = """FROM BASENAMESTRING = '%s' DO
			 TRAVERSE mAMa({'#role-basename'})
			 TRAVERSE aAMm({'#role-topic'})
		       DONE AS INDEXES""" % basename
		res = graph.STMQLExec(q)
		for i in res:
			t = TMObject(i,self)	
			result.append(t)
		return result

	def getAllWhereBaseNameContains(self,fragment):
		graph = self.graph
		result = []
		q = """FROM BASENAMESTRING LIKE '%%%s%%' DO
			 TRAVERSE mAMa({'#role-basename'})
			 TRAVERSE aAMm({'#role-topic'})
		       DONE AS INDEXES""" % fragment	
		res = graph.STMQLExec(q)
		for i in res:
			t = TMObject(i,self)	
			result.append(t)

		return result

	def getAllWhereResourceDataContains(self,fragment):
		graph = self.graph
		result = []
		q = """FROM RESOURCEDATA LIKE '%%%s%%' DO 
		       DONE AS INDEXES""" % fragment	
		res = graph.STMQLExec(q)
		for i in res:
			r = TMObject(i,self)	
			q2 = """FROM {%d} DO 
				  TRAVERSE mAMa({'#role-occurrence'})
				  TRAVERSE aAMm({'#role-topic'})
				 DONE AS INDEXES""" % i	
			res2 = graph.STMQLExec(q)
			assert(len(res2) > 0)
			t = TMObject(res2[0],self)	

			result.append( (t,r) )


		return result

	def getAllTemplates(self):
		graph = self.graph
		result = []
		q = """FROM {'#role-template'} DO
			 TRAVERSE rAMm({'#role-template'})
		       DONE AS INDEXES"""
		res = graph.STMQLExec(q)
		for i in res:
			t = TMObject(i,self)	
			result.append(t)

		return result

	def getAllAssociationTypes(self):
		graph = self.graph
		result = []
		q = """FROM ALL DO
			 TRAVERSE _AX_ 
		       DONE AS INDEXES"""
		res = graph.STMQLExec(q)
		for i in res:
			t = TMObject(i,self)	
			result.append(t)

		return result

	def getAllRoleRolePlayers(self):
		graph = self.graph
		result = []
		q = """FROM {'#role-role'} DO
			 TRAVERSE rAMm({'#role-role'})
		       DONE AS INDEXES"""
		res = graph.STMQLExec(q)
		for i in res:
			t = TMObject(i,self)	
			result.append(t)

		return result

	def getAllRoles(self):
		graph = self.graph
		result = []
		q = """FROM ALL DO
			 TRAVERSE mAMr(ANYROLE)
		       DONE AS INDEXES"""
		res = graph.STMQLExec(q)
		for i in res:
			t = TMObject(i,self)	
			result.append(t)

		return result

	def getAllTopLevelSuperClasses(self):
		graph = self.graph
		result = []
		q = """FROM {'#role-superclass'} DO
			 TRAVERSE rAMm({'#role-superclass'})
		       DONE AS INDEXES"""
		res = graph.STMQLExec(q)
		for i in res:
			q2 = """FROM {%d} DO
				  TRAVERSE mAMa({'#role-subclass'})
				DONE AS INDEXES""" % i

			res2 = graph.STMQLExec(q2)
			if(len(res2) != 0):
				continue

			t = TMObject(i,self)	
			result.append(t)

		return result

	def getAllTopLevelClasses(self):
		graph = self.graph
		result = []
		q = """FROM {'#role-superclass','#role-class'} DO
			TRAVERSE rAMm({'#role-superclass','#role-class'})
		       DONE AS INDEXES"""
		#q = """FROM {'#role-superclass'} DO
		#         TRAVERSE rAMm({'#role-superclass'})
		res = graph.STMQLExec(q)
		for i in res:
			q2 = """FROM {%d} DO
				  TRAVERSE mAMa({'#role-subclass'})
				DONE AS INDEXES""" % i

			res2 = graph.STMQLExec(q2)
			if(len(res2) != 0):
				continue

			t = TMObject(i,self)	
			result.append(t)

		return result

	def getAllClasses(self):
		graph = self.graph
		atTopicOccurrenceIndex = self.atTopicOccurrenceIndex
		result = []
		q = """FROM {'#role-class'} DO
			 TRAVERSE rAMm({'#role-class'})
		       DONE AS INDEXES"""
		res = graph.STMQLExec(q)
		for i in res:
			q2 = """FROM {%d} DO
				  TRAVERSE mAMa({'#role-class'})
				  TRAVERSE aAMm({'#role-instance'})
				  TRAVERSE _AX_ 
				DONE AS INDEXES""" % i

			res2 = graph.STMQLExec(q2)
			if(atTopicOccurrenceIndex in res2):
				continue
			q2 = """FROM {%d} DO
				  TRAVERSE mAMa({'#role-class'})
				  TRAVERSE aAMm({'#role-instance'})
				  TRAVERSE aAMm(ANYROLE) 
				DONE AS INDEXES""" % i

			res2 = graph.STMQLExec(q2)
			if(len(res2) != 0):
				continue
			t = TMObject(i,self)	
			result.append(t)

		return result


"""

get all top level classes
get all top level superclasses
get all occurrence types
get all templates with constraints
....

"""
		
class TMObject: 
	
	def __init__(self,arg,app):
		self.app = app
		self.index = 0
		self.subject = None
		if(isinstance(arg,types.IntType)):
			self.index = arg;
		else:
			sys.exit(1)	

	def getIndex(self):
		return self.index

	def getSCR(self):
		q = """FROM {%d} DO DONE""" % self.index	
		result = self.app.graph.STMQLExec(q)
		if(len(result) > 0):
			return result[0].getSCR()
		else:
			return None
	
	def getSIRs(self):
		q = """FROM {%d} DO DONE""" % self.index	
		t = self.app.graph.STMQLExec(q)
		result = self.app.graph.STMQLExec(q)
		if(len(result) > 0):
			return result[0].getSIRs()
		else:
			return []
 
 
		
	#----------------------------------
	# TBD: use scopes argument
	#----------------------------------
	def getBaseNames(self,scopes = []):
		q = """FROM {%d} DO 
                         TRAVERSE mAMa({'#role-topic'})
                         TRAVERSE aAMm({'#role-basename'})
                       DONE AS STRINGS""" % self.index	
		names = self.app.graph.STMQLExec(q)
		return names

	def getOccurringTopics(self,scopes = [], type = None):
		topics = []
		q = """FROM {%d} DO 
                         TRAVERSE mAMa({'#role-occurrence'})
                         TRAVERSE aAMm({'#role-topic'})
                       DONE AS INDEXES""" % self.index	
		result = self.app.graph.STMQLExec(q)
		for i in result:
			topics.append(TMObject(i,self.app))
		return topics

	def getOccurrenceResources(self,scopes = [], type = None):
		occs = []
		q = """FROM {%d} DO 
                         TRAVERSE mAMa({'#role-topic'})
                         TRAVERSE aAMm({'#role-occurrence'})
                       DONE""" % self.index	
		result = self.app.graph.STMQLExec(q)
		for r in result:
			occs.append(r.getSCR())
		return occs
	
	def getOccurrences(self,scopes = [], type = None):
		# this will be a tuples like (anode,type,occ-player)
		occs = []
		q = """FROM {%d} DO 
                         TRAVERSE mAMa({'#role-topic'})
                       DONE AS INDEXES""" % self.index	
		result = self.app.graph.STMQLExec(q)
		for r in result:
			q2 = """FROM {%d} DO 
                                  TRAVERSE _AX_ 
                                DONE AS INDEXES""" % r	
			result2 = self.app.graph.STMQLExec(q2)
			# continue if A node is not topic-occurrence
			if(len(result2) == 0 or result2[0] != self.app.atTopicOccurrenceIndex ):
				continue

			assoc_object = TMObject(r,self.app)
			classes = assoc_object.getClasses()
			if(len(classes) > 0):
				class_object = classes[0]
			else:
				class_object = None
			
			q2 = """FROM {%d} DO 
                                  TRAVERSE aAMm({'#role-occurrence'}) 
                                DONE AS INDEXES""" % assoc_object.index	
			result2 = self.app.graph.STMQLExec(q2)
			assert(len(result2) == 1)   # occ must be there

			occ_object = TMObject(result2[0],self.app)			 


			occs.append((assoc_object,class_object,occ_object))
		return occs


		q = """FROM {%d} DO 
                         TRAVERSE mAMa({'#role-topic'})
                         TRAVERSE aAMm({'#role-occurrence'})
                       DONE""" % self.index	
		result = self.app.graph.STMQLExec(q)
		for r in result:
			occs.append(r.getSCR())
		return occs


	
	def getPlayedRoles(self,scopes = [], type = None):
		roles = []
		q = """FROM {%d} DO 
                         TRAVERSE mAMr(ANYROLE)
                       DONE AS INDEXES""" % self.index	
		result = self.app.graph.STMQLExec(q)
		for i in result:
			roles.append(TMObject(i,self.app) )

		return roles

	def getClasses(self, scopes = []):
		classes = []
		q = """FROM {%d} DO 
                         TRAVERSE mAMa({'#role-instance'})
                         TRAVERSE aAMm({'#role-class'})
                       DONE AS INDEXES""" % self.index	
		result = self.app.graph.STMQLExec(q)
		for i in result:
			classes.append(TMObject(i,self.app))

		return classes
	
	def getSubclasses(self, scopes = []):
		classes = []
		q = """FROM {%d} DO 
                         TRAVERSE mAMa({'#role-superclass'})
                         TRAVERSE aAMm({'#role-subclass'})
                       DONE AS INDEXES""" % self.index	
		result = self.app.graph.STMQLExec(q)
		for i in result:
			classes.append(TMObject(i,self.app))

		return classes

	
	def getPlayers(self, scopes = []):
		players = []
		q = """FROM {%d} DO 
                         TRAVERSE rAMm({%d})
                       DONE AS INDEXES""" % (self.index,self.index)
		result = self.app.graph.STMQLExec(q)
		for i in result:
			players.append(TMObject(i,self.app))

		return players

	def getInstances(self, scopes = []):
		instances = []
		q = """FROM {%d} DO 
                         TRAVERSE mAMa({'#role-class'})
                         TRAVERSE aAMm({'#role-instance'})
                       DONE AS INDEXES""" % self.index	
		result = self.app.graph.STMQLExec(q)
		for i in result:
			instances.append(TMObject(i,self.app))

		return instances



"""

	def getOccurrences()
	
	def getSupeclasses()

	def getSubclasses()

	def getClasses()
	
	def getInstances()



	def getTemplate()


	def getPlayers()

	def getScopes()
"""	

# make the TMObject constructor available within GWApp
GWApp.TMObject_constructor = TMObject

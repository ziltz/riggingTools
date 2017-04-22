__author__ = 'Jerry'

import pymel.core as pm


'''


rig_ik( l_arm ,'l_armJA_JNT', 'l_handJA_JNT', 'ikRPsolver' )

'''
class rig_ik(object):

	def __init__(self, name, start, end, solver='ikSCsolver', **kwds):

		self.name = name
		self.start = start
		self.end = end
		self.solver = solver

		ikData = pm.ikHandle(n=self.name+'_ikHandle', sj=self.start, ee=self.end, solver=self.solver)
		self.handle = ikData[0]
		self.effector = ikData[1]







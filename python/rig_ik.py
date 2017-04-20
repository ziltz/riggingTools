__author__ = 'Jerry'



from rig_object import rig_object
from rig_utils import defaultReturn, defaultAppendReturn
from rig_transform import rig_transform

import pymel.core as pm

'''


rig_ik( l_arm ,'l_armJA_JNT', 'l_handJA_JNT', 'ikRPsolver' )

'''
class rig_ik(rig_object):

	def __init__(self, name, start, end, solver='ikSCsolver', **kwds):

		self.name = name
		self.start = start
		self.end = end
		self.solver = solver

		ikData = pm.ikHandle(n=self.name+'_ikHandle', sj=self.start, ee=self.end, solver=self.solver)
		self.handle = ikData[0]
		self.effector = ikData[1]

		super(rig_ik, self).__init__(self.handle, **kwds)






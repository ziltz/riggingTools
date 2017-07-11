


import pymel.core as pm


from rig_transform import rig_transform
from rig_utils import defaultReturn
from rutils.rig_nodes import *

'''

rig_measure(name='l_leg', start='locator1', end='locator2')


'''
class rig_measure(object):
	
	
	def __init__(self, **kwds):
		
		self.name = defaultReturn('rig_measure', 'name', param=kwds)
		self.start = defaultReturn(None, 'start', param=kwds)
		self.end = defaultReturn(None, 'end', param=kwds)
		self.parent = defaultReturn(None, 'parent', param=kwds)

		startConstrainer = self.start
		endConstrainer = self.end

		self.start = rig_transform( 0, name=self.name+'Start', type='locator', target=self.start ).object
		self.end = rig_transform( 0, name=self.name+'End', type='locator', target=self.end ).object
		
		pm.move(self.end, 0, 10, 0, r=True, os=True)
		
		#startAttr = pm.getAttr( self.start+'.translate' )
		startAttr = pm.xform(self.start, translation=True, query=True, ws=True)
		#endAttr = pm.getAttr( self.end+'.translate' )
		endAttr = pm.xform(self.end, translation=True, query=True, ws=True)
		self.shape = pm.distanceDimension(sp=startAttr, ep=endAttr)
		
		pm.move(self.end, 0, -10, 0, r=True, os=True)
		
		pm.rename(self.shape, self.name+'_distanceShape')
		self.distance = pm.rename(pm.listRelatives(self.shape, p=True)[0], self.name+'_distance')

		pm.pointConstraint( startConstrainer , self.start )
		pm.pointConstraint( endConstrainer , self.end )

		self.distanceVal = pm.getAttr(self.distance.distance)
		pm.addAttr(self.distance, longName='originalLength',
		           at='float', k=True, dv=self.distanceVal )
		self.distance.originalLength.set(cb=True)

		pm.addAttr(self.distance, longName='globalOriginalLength',
		           at='float', k=True, dv=self.distanceVal)
		self.distance.globalOriginalLength.set(cb=True)

		pm.addAttr(self.distance, longName='originalPercent',
		           at='float', k=True, dv=1)
		self.distance.originalPercent.set(cb=True)

		pm.addAttr(self.distance, longName='globalOriginalPercent',
		           at='float', k=True, dv=1)
		self.distance.globalOriginalPercent.set(cb=True)

		'''
		measurePnct = multiplyDivideNode(self.name + '_measurepcnt', 'divide',
		                   input1=[self.distance.distance,self.distance.distance, 1],
		                   input2=[self.distance.originalLength,self.distance.globalOriginalLength, 1],
		                   output=[self.distance.originalPercent, self.distance.globalOriginalPercent])
		'''
		print 'hey'
		measurePnct = multiplyDivideNode(self.name + '_measurepcnt', 'divide',
		                                 input1=[self.distance.distance, self.distance.distance, 1],
		                                 input2=[1, 1, 1],
		                                 output=[self.distance.originalPercent,
		                                         self.distance.globalOriginalPercent])

		# make 0.001 the minimum
		originalMin_con = conditionNode(self.name + '_origZeroMin', 'equal',
		                                          (self.distance, 'originalLength' ), ('', 0 ),
		                                          ( '', 0.001 ),
		                                          ( self.distance, 'originalLength'  ))
		globalOriginalMin_con = conditionNode(self.name + '_globalOrigZeroMin', 'equal',
		                                (self.distance, 'globalOriginalLength' ), ('', 0 ),
		                                ( '', 0.001 ),
		                                ( self.distance, 'globalOriginalLength'  ))

		pm.connectAttr( originalMin_con+'.outColorR', measurePnct+'.input2X' )
		pm.connectAttr( globalOriginalMin_con + '.outColorR', measurePnct + '.input2Y')

		if pm.objExists('rig_GRP'):
			multiplyDivideNode(self.name + '_globalOriginalLength', 'multiply',
			                   input1=[self.distance.originalLength, 0, 0],
			                   input2=['rig_GRP.worldScale', 0, 0],
			                   output=[self.distance.globalOriginalLength])


		if pm.objExists(self.parent):
			pm.parent( self.distance, self.start, self.end  ,self.parent )
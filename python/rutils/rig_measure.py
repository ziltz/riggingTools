


import pymel.core as pm


from rig_transform import rig_transform
from rig_utils import defaultReturn

'''

rig_measure(name='l_leg', start='locator1', end='locator2')


'''
class rig_measure(object):
	
	
	def __init__(self, **kwds):
		
		self.name = defaultReturn('rig_measure', 'name', param=kwds)
		self.start = defaultReturn(None, 'start', param=kwds)
		self.end = defaultReturn(None, 'end', param=kwds)
		                         
		self.start = rig_transform( 0, name=self.name+'Start', type='locator', target=self.start ).object
		self.end = rig_transform( 0, name=self.name+'End', type='locator', target=self.end ).object
		
		pm.move(self.end, 0, 10, 0, r=True, os=True)
		
		startAttr = pm.getAttr( self.start+'.translate' )
		endAttr = pm.getAttr( self.end+'.translate' )
		self.shape = pm.distanceDimension(sp=startAttr, ep=endAttr)
		
		pm.move(self.end, 0, -10, 0, r=True, os=True)
		
		pm.rename(self.shape, self.name+'_distanceShape')
		self.distance = pm.rename(pm.listRelatives(self.shape, p=True)[0], self.name+'_distance')



__author__ = 'Jerry'



from rutils.rig_object import rig_object
from rutils.rig_utils import *
from make.rig_controls import *
from rutils.rig_transform import rig_transform


import pymel.core as pm
import maya.cmds as cmds



'''

Create rig skeleton from root joint and given name

rigSkeleton = skeleton( 'test', 'mainJA_JNT' )

'''

class skeleton(rig_object):
	
	def __init__(self, character, root, **kwds):
		
		self.character = character
		self.root = root
		
		
		try:
			
			pm.select(cl=True)
			
			self.globalCtrl = rig_control(name='global', colour='white', shape='arrows',
			                              con=0, showAttrs=['sx', 'sy','sz'])
		
			self.topNode = rig_transform(0, name=self.character + 'RigSkeletonTop', child=self.globalCtrl.offset).object
			
			self.skeleton = rig_transform(0, name='skeleton', child=self.root, parent=self.globalCtrl.ctrl).object
			
			connectAttrToVisObj(self.globalCtrl.ctrl, 'skeletonVis', self.skeleton,
			                    defaultValue=1)
			
			pm.select(cl=True)
			
			self.sup = super(skeleton, self)
			self.sup.__init__(self.topNode, **kwds)
		
		except Exception as e:
			raise

		
		
		

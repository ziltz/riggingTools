__author__ = 'Jerry'


from rig_utils import defaultReturn
from rig_controls import *

class rig_puppet(object):
	
	def __init__(self, **kwds):
		
		self.globalCtrl = rig_control(name='global', con=0)
		
		self.character = defaultReturn('jerry', 'character', **kwds)
		
		self.topNode = rig_transform
		
		
	




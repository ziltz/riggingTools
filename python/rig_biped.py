

import sys
import pymel.core as pm
from rig_utils import defaultReturn


class rig_biped(object):
	
	def __init__(self, **kwds):
		self.arm = defaultReturn(['armJA_JNT'],'arm',**kwds)
		
		




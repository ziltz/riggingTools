

import sys
import pymel.core as pm

from rig_utils import defaultReturn
from rig_transform import rig_transform

class rig_biped(object):
	
	def __init__(self, **kwds):
		
		self.create()
		
	def create(self):
		
		self.spine()
		
		self.neck()
		
		self.head()
		
		for s in ['l', 'r']:
			self.arm(s, 'armJA_JNT', 'elbowJA_JNT', 'handJA_JNT')
			self.leg(s, 'legJA_JNT', 'kneeJA_JNT', 'footJA_JNT')
			self.shoulder(s, )
			
		self.hip()
		
					
		return
	
	def arm(self, side, arm, elbow, hand):
		
		arm = side+'_'+arm
		elbow = side+'_'+elbow
		hand = side+'_'+hand
		
		chain = [arm, elbow, hand]
		
		return
	
	def shoulder(self, side, ):
		
		return
		
	def hip(self):
		return
	
	def leg(self, side, leg, knee, foot):
		return
	
	def spine(self):
		return
		
	def neck(self):
		return
		
	def head(self):
		return
		




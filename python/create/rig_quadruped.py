__author__ = 'Jerry'


from make.rig_ik import rig_ik
from rutils.rig_chain import *
from make.rig_controls import *
from rutils.rig_modules import rig_module
from rutils.rig_transform import rig_transform


class rig_quadruped(object):

	def __init__(self, **kwds):

		self.globalCtrl = pm.PyNode('global_CTRL')

		self.scapula = 'scapulaJA_JNT'

		self.armName = 'armJA_JNT'
		self.elbowName = 'elbowJA_JNT'
		self.handName = 'handJA_JNT'

		self.spineModule = ''
		self.neckModule = ''
		self.headModule = ''
		self.shoulderModule = ''
		self.armModule = ''
		self.legModule = ''


	def create(self):

		self.spine()

		self.neck()

		self.head()

		for s in ['l', 'r']:
			self.shoulder(s)
			self.arm(s)
			self.leg(s)

		self.hip()


		return

	def spine (self):
		return

	def neck (self):
		return

	def head (self):
		return

	def shoulder (self, side):
		return

	def pelvis (self):
		return

	def arm (self, side, ctrlSize = 1):
		return

	def leg (self, side):
		return
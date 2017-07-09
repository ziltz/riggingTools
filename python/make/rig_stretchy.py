__author__ = 'Jerry'

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mm

from rutils.rig_transform import *
from rutils.rig_measure import *
from rutils.rig_nodes import *
from rutils.rig_name import *
from rutils.rig_constraint import *

'''

lArmStretchy = rig_makeStretchy( 'l_arm', start, end, up)


'''
class rig_makeStretchy( object ):


	def __init__(self, name, start, end, up, **kwds):

		rigGrp = ''
		if cmds.objExists('rig_GRP'):
			rigGrp = 'rig_GRP'

		parent = 'stretchyJoints_GRP'
		if not cmds.objExists(parent):
			parent = rig_transform(0, name='stretchyJoints', parent=rigGrp).object

		self.topGrp = rig_transform(0, name=name+'Stretchy',
		                         parent=parent).object
	
	
		jntStart = rig_transform(0, name=name + 'JntStartTmp',type='joint', target=start).object
		jntEnd = rig_transform(0, name=name + 'JntEndTmp', type='joint', target=end,parent=jntStart).object
		cmds.joint( jntStart, e=True, oj='xzy', sao='zup', ch=True, zso=True )
	
		pm.setAttr( jntEnd+'.jointOrientX', 0 )
		pm.setAttr( jntEnd+'.jointOrientY', 0 )
		pm.setAttr( jntEnd+'.jointOrientZ', 0 )
	
		self.startOffset = rig_transform(0, name=name + 'DrvStartOffset',
		                         parent=self.topGrp, target=jntStart).object
		self.start = rig_transform(0, name=name + 'DrvStart', type='locator',
		                         parent=self.startOffset, target=self.startOffset).object
		startLoc = rig_transform(0, name=name+'StartStretchy', type='locator',
		                             parent=self.topGrp, target=jntStart).object
	
		self.endOffset = rig_transform(0, name=name + 'DrvEndOffset',
		                            parent=self.topGrp, target=jntEnd).object
		self.end = rig_transform(0, name=name + 'DrvEnd', type='locator',
		                       parent=self.endOffset, target=self.endOffset).object
		endLoc = rig_transform(0, name=name+'EndStretchy', type='locator',
		                           parent=self.topGrp, target=jntEnd).object
	
		self.upOffset = rig_transform(0, name=name + 'DrvUpOffset',
		                          parent=self.topGrp, target=up).object
	
		pm.delete(jntStart, jntEnd)
	
		partsGrp = mm.eval('rig_makePiston("' + startLoc + '", "' + endLoc + '", "' + name +
		                         'StretchyParts");')
	
		pm.hide(partsGrp)
	
		pm.delete(pm.parentConstraint(self.upOffset, endLoc + 'Up'))
		pm.parent(endLoc + 'Up',  self.upOffset)
		self.up = name+'DrvUp_LOC'
		pm.rename(endLoc+'Up', name + 'DrvUp_LOC')
	
		self.startJnt = startLoc.replace('_LOC', '_JNT')
		endJnt = endLoc.replace('_LOC', '_JNT')
	
		pm.parent (endJnt, self.startJnt)
		pm.parent( self.startJnt, self.topGrp)
		pm.parentConstraint( startLoc+'Aim', self.startJnt, mo=True  )
		pm.delete(startLoc + 'Up', endLoc, startLoc)
	
		pm.parentConstraint( self.start, startLoc+'AimOffset',mo=True )
		pm.parentConstraint( self.end, endLoc+'AimOffset',mo=True )
		pm.parentConstraint( self.start, self.upOffset, mo=True )
	
		pm.parent(partsGrp, self.topGrp)
	
		measure = rig_measure(name=name+'Dist', start=self.start, end=self.end,
		                        parent=partsGrp)
	
		# make pin feature
	
		#pm.connectAttr( measure.distance.globalOriginalPercent, self.startJnt+'.scaleX' )

		self.startJnt = pm.PyNode(self.startJnt)
		pm.addAttr(self.startJnt, longName='stretch',
		           at='float', k=True, dv=1, min=0, max=1)
		#self.startJnt.stretch.set(cb=True)

		bldColor = pm.shadingNode('blendColors', asUtility=True,
		                          name=name + '_blendStretch')

		pm.connectAttr(measure.distance.globalOriginalPercent, bldColor + '.color1R',
		               f=True)  # connect ik jnt to color
		pm.setAttr (  bldColor + '.color2R', 1 )
		pm.connectAttr(bldColor + '.outputR',self.startJnt+'.scaleX',
		               f=True)  # connect bldColor output to bind jnt

		pm.connectAttr(self.startJnt.stretch, bldColor.blender)

	


def rig_stretchyMirror(topGroup):

	listParts = cmds.listRelatives(topGroup)

	nameBase = topGroup.replace('Stretchy_GRP', '')

	tokens = nameBase.split('_')
	side = tokens[0]

	mirrorSide = rig_nameGetMirror(nameBase)
	name = mirrorSide+'_'+tokens[1]

	mirrorGrp = rig_transform(0, name='mirrorTmp').object
	start = ''
	end = ''
	up = ''
	startCons = {}
	endCons = {}
	upCons = {}
	for part in listParts:
		if 'DrvStart' in part:
			start = rig_transform(0, name='startTmp',type='locator' ,target=part, parent =mirrorGrp).object
			try:
				offsetCon = pm.listRelatives(part, type='constraint')[0]
				targets = []
				for o in offsetCon.getTargetList():
					print 'side targets = '+o
					print rig_nameMirror(o.stripNamespace())
					targets.append(rig_nameMirror(o.stripNamespace()))
				startCons['offset'] = targets
				startCons['offsetCon'] = offsetCon.type()
			except IndexError:
				print 'no constraints'

			loc = cmds.listRelatives(part, type='transform')[0]
			try:
				locCon = pm.listRelatives(loc, type='constraint')[0]
				targets = []
				for o in locCon.getTargetList():
					targets.append(rig_nameMirror(o.stripNamespace()))
				startCons['loc'] = targets
				startCons['locCon'] = locCon.type()
			except IndexError:
				print 'no constraints'
		if 'DrvEnd' in part:
			end = rig_transform(0, name='endTmp', type='locator', target=part, parent=mirrorGrp).object
			try:
				offsetCon = pm.listRelatives(part, type='constraint')[0]
				targets = []
				for o in offsetCon.getTargetList():
					print 'side targets = ' + o
					print rig_nameMirror(o.stripNamespace())
					targets.append(rig_nameMirror(o.stripNamespace()))
				endCons['offset'] = targets
				endCons['offsetCon'] = offsetCon.type()
			except IndexError:
				print 'no constraints'

			loc = cmds.listRelatives(part, type='transform')[0]
			try:
				locCon = pm.listRelatives(loc, type='constraint')[0]
				targets = []
				for o in locCon.getTargetList():
					targets.append(rig_nameMirror(o.stripNamespace()))
				endCons['loc'] = targets
				endCons['locCon'] = locCon.type()
			except IndexError:
				print 'no constraints'
		if 'DrvUp' in part:
			up = rig_transform(0, name='upTmp', type='locator', target=part, parent=mirrorGrp).object
			try:
				offsetCon = pm.listRelatives(part, type='constraint')[0]
				targets=[]
				for o in offsetCon.getTargetList():
					targets.append( rig_nameMirror(o.stripNamespace()) )
				upCons['offset'] = targets
				upCons['offsetCon'] = offsetCon.type()
			except IndexError:
				print 'no constraints'

			loc = cmds.listRelatives(part, type='transform')[0]
			try:
				locCon = pm.listRelatives(loc, type='constraint')[0]
				targets = []
				for o in locCon.getTargetList():
					targets.append(rig_nameMirror(o.stripNamespace()))
				upCons['loc'] = targets
				upCons['locCon'] = locCon.type()
			except IndexError:
				print 'no constraints'

	pm.setAttr(mirrorGrp+'.scaleX', -1)

	stretchy = rig_makeStretchy( name, start, end, up)

	try:
		print startCons['offset']
		rig_constrainByType(startCons['offsetCon'], startCons['offset'], stretchy.startOffset)
	except KeyError:
		print 'no key'
	try:
		rig_constrainByType(startCons['locCon'], startCons['loc'], stretchy.start)
	except KeyError:
		print 'no key'
	try:
		rig_constrainByType(endCons['offsetCon'], endCons['offset'], stretchy.endOffset)
	except KeyError:
		print 'no key'
	try:
		rig_constrainByType(endCons['locCon'], endCons['loc'], stretchy.end)
	except KeyError:
		print 'no key'
	try:
		rig_constrainByType(upCons['offsetCon'], upCons['offset'], stretchy.upOffset)
	except KeyError:
		print 'no key'
	try:
		rig_constrainByType(upCons['locCon'], upCons['loc'], stretchy.up)
	except KeyError:
		print 'no key'

	pm.delete(mirrorGrp)




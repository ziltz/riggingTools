__author__ = 'Jerry'


import pymel.core as pm

def blendColors(objA, objB, objResult, name='', driverAttr='', attribute=''):
	bldColor = pm.shadingNode('blendColors', asUtility=True,
	                          name=name +'_blendColor')

	print 'object A ' + objA
	print  'object B ' +objB
	print  'object result ' +objResult

	print  'driverAttr ' + driverAttr

	print  'attribute ' + attribute

	"Select ik, fk then bind joints in this order"

	pm.connectAttr( objA+ '.'+attribute, bldColor + '.color1',
	               f=True)  # connect ik jnt to color1
	pm.connectAttr( objB + '.'+attribute, bldColor + '.color2',
	               f=True)  # connect fk jnt to color2
	pm.connectAttr( bldColor + '.output', objResult + '.rotate',
	               f=True)  # connect bldColor output to bind jnt

	pm.connectAttr(driverAttr, bldColor.blender)
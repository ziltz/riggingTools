__author__ = 'Jerry'


import pymel.core as pm
import maya.cmds as cmds

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

'''

multiplyDivideNode( 'legRotate', 'multiply', input1=[0,0,0], input2=[0,0,0],
output=[])

'''
def multiplyDivideNode( name='multiplyDivide', operation='multiply', input1=(0,0,0),
                     input2=(0,0,0), output=[] ):
	node = pm.shadingNode('multiplyDivide', asUtility=True)
	mdNode = pm.rename(node, name+'_MD')

	xyz = ('X', 'Y', 'Z')

	for i in range(0,3):
		print 'input1 = '+str(input1[i])
		print type(input1[i])
		try:
			pm.setAttr(mdNode + '.input1'+xyz[i], input1[i])
		except RuntimeError:
			pm.connectAttr(input1[i], mdNode + '.input1' + xyz[i], f=True)

		print 'input2 = ' + str(input2[i])
		try:
			pm.setAttr(mdNode + '.input2' + xyz[i], input2[i])
		except RuntimeError:
			pm.connectAttr(input2[i], mdNode + '.input2' + xyz[i], f=True)

		pm.connectAttr( mdNode + '.output' + xyz[i],  output[i] ,f=True)

	if operation == 'multiply':
		pm.setAttr( mdNode+'.operation', 1 )
	if operation == 'divide':
		pm.setAttr( mdNode+'.operation', 2 )
	if operation == 'power':
		pm.setAttr( mdNode+'.operation', 3 )

	return mdNode


def connectReverse( name='reverseNode#', input=(0,0,0), output=(0,0,0) ):

	node = pm.shadingNode('reverse', asUtility=True)
	reverseNode = pm.rename(node, name + '_RVRSE')

	xyz = ('X', 'Y', 'Z')

	for i in range(0, 3):
		try:
			pm.connectAttr(input[i], reverseNode + '.input' + xyz[i], f=True)
		except RuntimeError:
			print 'cannot find attribute '+str(input[i])

		try:
			pm.connectAttr(reverseNode + '.output' + xyz[i],output[i] ,f=True)
		except RuntimeError:
			print 'cannot find attribute ' + str(output[i])

	return reverseNode
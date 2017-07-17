__author__ = 'Jerry'


import pymel.core as pm
import maya.cmds as cmds

def blendColors(objA, objB, objResult, name='', driverAttr='', attribute=''):
	bldColor = pm.shadingNode('blendColors', asUtility=True,
	                          name=name +'_blendColor')


	"Select ik, fk then bind joints in this order"

	pm.connectAttr( objA+ '.'+attribute, bldColor + '.color1',
	               f=True)  # connect ik jnt to color1
	pm.connectAttr( objB + '.'+attribute, bldColor + '.color2',
	               f=True)  # connect fk jnt to color2
	pm.connectAttr( bldColor + '.output', objResult + '.'+attribute,
	               f=True)  # connect bldColor output to bind jnt

	pm.connectAttr(driverAttr, bldColor.blender)



'''

multiplyDivideNode( 'legRotate', 'multiply', input1=[0,0,0], input2=[1,1,1],
output=[])

'''
def multiplyDivideNode( name='multiplyDivide', operation='multiply', input1=(0,0,0),
                     input2=(1,1,1), output=[] ):
	node = pm.shadingNode('multiplyDivide', asUtility=True)
	mdNode = pm.rename(node, name+'_MD')

	xyz = ('X', 'Y', 'Z')

	for i in range(0,3):
		try:
			pm.setAttr(mdNode + '.input1'+xyz[i], input1[i])
		except RuntimeError:
			pm.connectAttr(input1[i], mdNode + '.input1' + xyz[i], f=True)

		try:
			pm.setAttr(mdNode + '.input2' + xyz[i], input2[i])
		except RuntimeError:
			pm.connectAttr(input2[i], mdNode + '.input2' + xyz[i], f=True)

		try:
			pm.connectAttr( mdNode + '.output' + xyz[i],  output[i] ,f=True)
		except IndexError:
			pass

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


def connectNegative( obj1, obj2, name='connectNegative#' ):

	negativeNode = multiplyDivideNode(name, 'multiply', input1=[obj1, 0, 0],
	                                input2=[-1, -1,-1],
	                   output=[obj2])

	return negativeNode


def multDoubleLinear( in1, in2, out, name='multDoubleLinear#'):

	mdl = pm.shadingNode('multDoubleLinear', asUtility=True)
	mdlNode = pm.rename(mdl, name+'_MDL')

	try:
		pm.connectAttr(in1, mdlNode+'.input1', f=True)
	except RuntimeError:
		print 'cannot find attribute ' + str(in1)

	try:
		pm.connectAttr(in2, mdlNode + '.input2', f=True)
	except RuntimeError:
		print 'cannot find attribute ' + str(in2)

	try:
		pm.connectAttr( mdlNode + '.output',out, f=True)
	except RuntimeError:
		print 'cannot find attribute ' + str(out)

	return mdlNode

'''

OLD NODES FROM OLD RIGGING TOOLS UNI DAYS LOL

'''

def plusMinusNode( name, operation, inputNme1, input1, inputNme2, input2 ):
	node = cmds.shadingNode('plusMinusAverage', asUtility=True)
	avgNode = cmds.rename(node, name+'_plusMinAvg')
	if not inputNme1:
		cmds.setAttr( avgNode+'.input1D[0]', input1 )
	else:
		cmds.connectAttr( inputNme1+'.'+input1 ,avgNode+'.input1D[0]', f=True )

	if not inputNme2:
		cmds.setAttr( avgNode+'.input1D[1]', input2 )
	else:
		cmds.connectAttr( inputNme2+'.'+input2 ,avgNode+'.input1D[1]', f=True )


	if operation == 'sum':
		cmds.setAttr( avgNode+'.operation', 1 )
	else:
		cmds.setAttr( avgNode+'.operation', 2 )

	return avgNode



def globalFixNode( _nodeMDNme, _fixNode, _fixNodeAttr ):
    globalMDNode = multiDivideNode( _nodeMDNme, 'divide', _fixNode, _fixNodeAttr, 'rig_GRP',
                                    'worldScale' )
    return globalMDNode



def multiDivideNode( _nme, _operation, _inputNme1, _input1, _inputNme2, _input2 ):
    node = cmds.shadingNode('multiplyDivide', asUtility=True)
    mdNode = cmds.rename(node, _nme+'_MD')

    if not _inputNme1:
        cmds.setAttr( mdNode+'.input1X', _input1 )
    else:
        cmds.connectAttr( _inputNme1+'.'+_input1 ,mdNode+'.input1X', f=True )
    if not _inputNme2:
        cmds.setAttr( mdNode+'.input2X', _input2 )
    else:
        cmds.connectAttr( _inputNme2+'.'+_input2 ,mdNode+'.input2X', f=True )

    if _operation == 'multiply':
        cmds.setAttr( mdNode+'.operation', 1 )
    if _operation == 'divide':
        cmds.setAttr( mdNode+'.operation', 2 )
    if _operation == 'power':
        cmds.setAttr( mdNode+'.operation', 3 )

    return mdNode

def conditionNode( _nme, _operation, _firstTerm, _secondTerm, _ifTrue, _ifFalse ):
    node = cmds.shadingNode('condition', asUtility=True)
    conditionNode = cmds.rename(node, _nme+'_condition')

    if not _firstTerm[0]:
        cmds.setAttr( conditionNode+'.firstTerm', _firstTerm[1] )
    else:
        cmds.connectAttr( _firstTerm[0]+'.'+_firstTerm[1] ,conditionNode+'.firstTerm', f=True )

    if not _secondTerm[0]:
        cmds.setAttr( conditionNode+'.secondTerm', _secondTerm[1] )
    else:
        cmds.connectAttr( _secondTerm[0]+'.'+_secondTerm[1] ,conditionNode+'.secondTerm', f=True )

    if not _ifTrue[0]:
        cmds.setAttr( conditionNode+'.colorIfTrue.colorIfTrueR', _ifTrue[1] )
    else:
        cmds.connectAttr( _ifTrue[0]+'.'+_ifTrue[1] ,conditionNode+'.colorIfTrue.colorIfTrueR', f=True )

    if not _ifFalse[0]:
        cmds.setAttr( conditionNode+'.colorIfFalse.colorIfFalseR', _ifFalse[1] )
    else:
        cmds.connectAttr( _ifFalse[0]+'.'+_ifFalse[1] ,conditionNode+'.colorIfFalse.colorIfFalseR', f=True )

    if _operation == 'greater than':
        cmds.setAttr( conditionNode+'.operation', 2 )
    if _operation == 'equal':
        cmds.setAttr( conditionNode+'.operation', 0 )
    if _operation == 'less than':
        cmds.setAttr( conditionNode+'.operation', 4 )
    # in future use need to add a switch or dictionary
    # to use other operations. In a rush, don't hate me future jerry :<
    return conditionNode


'''

END OF  NODES FROM OLD RIGGING TOOLS UNI DAYS LOL

'''




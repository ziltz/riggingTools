__author__ = 'Jerry'


from rutils.rig_utils import *
from rutils.rig_nodes import *
from rutils.rig_measure import *
from rutils.rig_transform import *
from rutils.rig_anim import *
from make.rig_controls import *

import pymel.core as pm
import maya.mel as mm
import maya.cmds as cmds

'''


rig_ik( l_arm ,'l_armJA_JNT', 'l_handJA_JNT', 'ikRPsolver' )

ikSpringSolver

'''
class rig_ik(object):

	def __init__(self, name, start, end, solver='ikSCsolver', **kwds):

		self.name = name
		self.start = start
		self.end = end
		self.solver = solver

		self.numSpans = defaultReturn(1, 'numSpans', param=kwds)

		if self.solver == 'ikSpringSolver':
			mm.eval("ikSpringSolver;")
		
		ikData = pm.ikHandle(n=self.name+'_ikHandle', sj=self.start, ee=self.end,
		                     solver=self.solver, ns=self.numSpans)
		self.handle = ikData[0]
		self.effector = ikData[1]
		self.curve = ''
		try:
			self.curve = pm.rename( ikData[2], self.name+'SplineIK_CRV')
			pm.parent(self.curve, w=True)
			pm.setAttr(self.curve + '.inheritsTransform', 0)
			pm.setAttr(self.handle + '.twistType', 2) # ease out
			pm.setAttr(self.handle + '.rootTwistMode', 1)  # root twist mode
		except IndexError:
			print 'Not a spline IK'

	def poleVectorConstraint(self):
		return



def rig_ikStretchySoftPop(side, name, chainIK, module, ikCtrl, ctrlSize, topGrp):

	# assign appropriate names
	startJnt = chainIK[0]
	midJnt = chainIK[1]
	endJnt = chainIK[2]

	nme = name
	if name.startswith('l_'):
		nme = name.replace('l_', '')
	if name.startswith('r_'):
		nme = name.replace('r_', '')

	midPinControl = rig_control(side=side, name=nme+'MidPin', shape='sphere', modify=1,
	                             parentOffset=module.controlsSec, scale=ctrlSize,
	                             rotateOrder=2, lockHideAttrs=['rx', 'ry', 'rz'])

	pm.delete(pm.parentConstraint( midJnt, midPinControl.offset  ))
	pm.parentConstraint( topGrp, midPinControl.offset, mo=True )

	startMeasure = rig_transform(0, name=name + '_startMeasure', type='locator',
	                         parent=module.parts, target=topGrp).object

	pm.pointConstraint( topGrp, startMeasure )
	pm.aimConstraint(ikCtrl.con, startMeasure)

	endMeasure = rig_transform(0, name=name + '_endMeasure', type='locator',
	                             parent=module.parts, target=ikCtrl.gimbal.ctrl).object

	pm.pointConstraint( ikCtrl.con, endMeasure )

	measureGrp = rig_transform(0, name=name + '_measureSetup',
	                           parent=module.parts).object

	upperDist = rig_measure(name=name+'Upper', start=startMeasure, end=midPinControl.con,
	                        parent=measureGrp)
	lowerDist = rig_measure(name=name + 'Lower', start=midPinControl.con, end=endMeasure,
	                        parent=measureGrp)
	totalDist = rig_measure(name=name + 'Total', start=startMeasure, end=endMeasure,
	                        parent=measureGrp)

	endBlendLoc = rig_transform(0, name=name + '_endBlend', type='locator',
	                             parent=module.parts, target=endJnt).object

	endSoftOffset = rig_transform(0, name=name + '_endSoftOffset',
	                              parent=module.parts, target=endJnt).object

	pm.parentConstraint( startMeasure, endSoftOffset )
	endSoftLoc = rig_transform(0, name=name + '_endSoft', type='locator',
	                           parent=endSoftOffset, target=ikCtrl.gimbal.ctrl).object

	#wristPC = pm.pointConstraint(endSoftLoc, endBlendLoc, mo=True, w=0)
	#stretchPC = pm.pointConstraint(endMeasure, endBlendLoc, mo=True, w=1)
	stretchPC = pm.pointConstraint(endMeasure,endSoftLoc, endBlendLoc, mo=True)
	stretchTargets = stretchPC.getWeightAliasList()
	pm.setAttr( stretchTargets[1], 0 )
	#pm.pointConstraint( endBlendLoc, ikCtrl.con, mo=True)

	endBlendDist = rig_measure(name=name + 'EndBlend', start=startMeasure, end=endBlendLoc,
	                           parent=measureGrp)
	endSoftBlendDist = rig_measure(name=name + 'SoftEndBlend', start=endSoftLoc, end=endBlendLoc,
	                               parent=measureGrp)

	pm.addAttr(ikCtrl.ctrl, ln='ikSettings', at='enum',
	             enumName='___________',
	             k=True)
	ikCtrl.ctrl.ikSettings.setLocked(True)
	blendAttrNodes_and_checkStretchCond = addStretchyIKJoints(name, chainIK, (upperDist.distance,
	                                                                    lowerDist.distance,
	                                                                    totalDist.distance),
	                                                          ikCtrl.ctrl,
	                                                          (endBlendDist.distance,
	                                                           endSoftBlendDist.distance))

	# create sdk for elbow pin
	upperBlendNode = blendAttrNodes_and_checkStretchCond[0]
	lowerBlendNode = blendAttrNodes_and_checkStretchCond[1]
	checkStretch_condition = blendAttrNodes_and_checkStretchCond[2]
	cmds.connectAttr(checkStretch_condition + '.outColorR', endSoftLoc + '.translateX', f=True)
	pm.addAttr(midPinControl.ctrl, longName='pin', attributeType="double",
	             min=0, max=10, defaultValue=0, keyable=True)

	rig_animDrivenKey(midPinControl.ctrl.pin, (0, 10),
	                  upperBlendNode + '.attributesBlender', (0, 1 ))
	rig_animDrivenKey(midPinControl.ctrl.pin, (0, 10),
	                  lowerBlendNode + '.attributesBlender', (0, 1 ))

	rig_animDrivenKey(ikCtrl.ctrl.ikStretch, (0, 1),
	                  stretchTargets[1], (1, 0 ))
	rig_animDrivenKey(ikCtrl.ctrl.ikStretch, (1, 0),
	                  stretchTargets[0], (1, 0 ))

	return endBlendLoc

def addStretchyIKJoints( _name, _jntList, _distanceDim, _ikControl, _wristStretchDist ):
    print 'addStretchyIKJoints function starts here ------------------------'
    # assign appropriate names
    nme = _name+'ikStretchy'
    upperDistDim = _distanceDim[0]
    lowerDistDim = _distanceDim[1]
    ctrlDistDim = _distanceDim[2]
    armJnt = _jntList[0]
    elbowJnt = _jntList[1]
    handJnt = _jntList[2]
    wristStretchDist = _wristStretchDist[0]
    wristSoftBlendDist = _wristStretchDist[1]

    _ikControl = _ikControl.stripNamespace()

    cmds.addAttr( _ikControl, longName='ikStretch', shortName='iks',attributeType="double",
                                min=0, max=1, defaultValue=0, keyable=True )
    cmds.addAttr( _ikControl, longName='ikSoftBlend', shortName='iksb',attributeType="double",
                                min=0, max=1, defaultValue=0.2, keyable=True )
    cmds.addAttr( _ikControl, longName='elbowSlide', shortName='es',attributeType="double",
                                min=-1, max=1, defaultValue=0, keyable=True )

    # get upper and lower distance and sum them to store as fixed values
    upperDist = cmds.getAttr( upperDistDim+'.distance' )
    lowerDist = cmds.getAttr( lowerDistDim+'.distance' )
    ctrlDist = cmds.getAttr( ctrlDistDim+'.distance' )
    upAndLowDist = upperDist + lowerDist

    elbowX = cmds.getAttr( elbowJnt+'.translateX' )
    handX = cmds.getAttr( handJnt+'.translateX' )

    # Create Soft Blend Nodes for stretchy

    global_ctrlDist_MD = globalFixNode( nme+'_globalScale_ctrlDist', ctrlDistDim, 'distance' )

    totalDist_min_softDist_PM = plusMinusNode( nme+'_totalDist_min_softDist', 'subtract',
                             '', upAndLowDist, _ikControl,'ikSoftBlend' )

    ctrlDist_minus_softDist_PM = plusMinusNode( nme+'_ctrlDist_minus_softDist', 'subtract',
                    global_ctrlDist_MD, 'outputX', totalDist_min_softDist_PM, 'output1D' )

    stretchDivsion_DIV_MD = multiDivideNode( nme+'_stretchDivision_DIV', 'divide',
                        ctrlDist_minus_softDist_PM, 'output1D', _ikControl, 'ikSoftBlend' )

    correctValue_MULT_MD = multiDivideNode( nme+'_correctValue_MULT', 'multiply',
                        '', -1, stretchDivsion_DIV_MD, 'outputX' )

    correctValue_expo_POW_MD = multiDivideNode( nme+'_correctValue_expo_POW', 'power',
                        '', 2.718282, correctValue_MULT_MD, 'outputX' )

    exponent_softBlend_MULT_MD = multiDivideNode( nme+'_exponent_softBlend_MULT', 'multiply',
                        _ikControl, 'ikSoftBlend', correctValue_expo_POW_MD, 'outputX' )

    totalDist_minus_exponent_PM = plusMinusNode( nme+'_totalDist_minus_exponent', 'subtract',
                    '', upAndLowDist, exponent_softBlend_MULT_MD, 'outputX' )

    aPointLessCheck_condition = conditionNode( nme+'_aPointLessCheck', 'greater than',
                            (_ikControl, 'ikSoftBlend' ), ('', 0 ),
                            ( totalDist_minus_exponent_PM, 'output1D' ), ( '', upAndLowDist ) )

    checkStretch_condition = conditionNode( nme+'_checkStretch', 'greater than',
                            (global_ctrlDist_MD, 'outputX' ), (totalDist_min_softDist_PM, 'output1D' ),
                            ( aPointLessCheck_condition, 'outColorR' ), ( global_ctrlDist_MD, 'outputX' ) )

    # create upper and lower elbow pin

    globalFix_wristSoftDist_MD = globalFixNode( nme+'_globalFix_wristSoftDist', wristSoftBlendDist, 'distance' )

    upperDist_divide_totalDist_MD = multiDivideNode( nme+'_upperDist_divide_totalDist', 'divide',
                        '', upperDist, '', upAndLowDist )

    lowerDist_divide_totalDist_MD = multiDivideNode( nme+'_lowerDist_divide_totalDist', 'divide',
                        '', lowerDist, '', upAndLowDist )

    ###
    # slide nodes
    globalFix_wristStretchDist_MD = globalFixNode( nme+'_globalFix_wristStretchDist', wristStretchDist, 'distance' )

    stretchDist_GThan_totalDist_condition = conditionNode( nme+'stretchDist_GThan_totalDist', 'greater than',
                            ( globalFix_wristStretchDist_MD, 'outputX' ), ('', upAndLowDist ),
                            ( globalFix_wristStretchDist_MD, 'outputX' ), ( '', upAndLowDist ) )

    upper_stretchDist_divUpLow_MD = multiDivideNode( nme+'upper_stretchDist_divUpLow', 'multiply',
                   stretchDist_GThan_totalDist_condition, 'outColorR', upperDist_divide_totalDist_MD, 'outputX' )

    lower_stretchDist_divUpLow_MD = multiDivideNode( nme+'lower_stretchDist_divUpLow', 'multiply',
                   stretchDist_GThan_totalDist_condition, 'outColorR', lowerDist_divide_totalDist_MD, 'outputX' )

    upper_slideSwitch_MD = multiDivideNode( nme+'upper_slideSwitch', 'multiply',
                   upper_stretchDist_divUpLow_MD, 'outputX', _ikControl, 'elbowSlide' )

    lower_slideSwitch_MD = multiDivideNode( nme+'lower_slideSwitch', 'multiply',
                   lower_stretchDist_divUpLow_MD, 'outputX', _ikControl, 'elbowSlide' )


    ###
    # find middle and add/subtract lower and upper bounds

    upperDist_mult_softBlend_MD = multiDivideNode( nme+'_upperDist_mult_softBlend', 'multiply',
                        globalFix_wristSoftDist_MD, 'outputX', upperDist_divide_totalDist_MD, 'outputX' )

    lowerDist_mult_softBlend_MD = multiDivideNode( nme+'_lowerDist_mult_softBlend', 'multiply',
                       globalFix_wristSoftDist_MD, 'outputX', lowerDist_divide_totalDist_MD, 'outputX' )

    upper_stretchSwitch_MD = multiDivideNode( nme+'_lowerDist_divide_totalDist', 'multiply',
                        upperDist_mult_softBlend_MD, 'outputX', _ikControl, 'ikStretch' )

    lower_stretchSwitch_MD = multiDivideNode( nme+'_lower_stretchSwitch', 'multiply',
                        lowerDist_mult_softBlend_MD, 'outputX', _ikControl, 'ikStretch' )

    upper_add_stretchDist_PM = plusMinusNode( nme+'_upper_add_stretchDist', 'sum',
                    upper_stretchSwitch_MD, 'outputX', '', upperDist )

    lower_add_stretchDist_PM = plusMinusNode( nme+'_lower_add_stretchDist', 'sum',
                       lower_stretchSwitch_MD, 'outputX', '', lowerDist )

    ###
    # slide nodes
    upper_lower_switch_condition = conditionNode( nme+'upper_lower_switch', 'less than',
                            ( _ikControl, 'ikSoftBlend' ), ('', 0 ),
                            ( upper_slideSwitch_MD, 'outputX' ), ( lower_slideSwitch_MD, 'outputX' ) )

    upper_add_stretchLower_PM = plusMinusNode( nme+'_lower_add_stretchDist', 'sum',
                       upper_add_stretchDist_PM, 'output1D', upper_lower_switch_condition, 'outColorR' )

    lower_minus_stretchUpper_PM = plusMinusNode( nme+'_lower_add_stretchDist', 'subtract',
                       lower_add_stretchDist_PM, 'output1D', upper_lower_switch_condition, 'outColorR' )

    upper_add_lower_PM = plusMinusNode( nme+'upper_add_lower', 'sum',
                       '', upperDist, upper_lower_switch_condition, 'outColorR' )

    lower_minus_upper_PM = plusMinusNode( nme+'lower_minus_upper', 'subtract',
                       '', lowerDist, upper_lower_switch_condition, 'outColorR' )

    global_upperDist_MD = globalFixNode( nme+'global_upperDist', upperDistDim, 'distance' )
    global_lowerDist_MD = globalFixNode( nme+'global_lowerDist', lowerDistDim, 'distance' )

    upper_elbowPin_condition = conditionNode( nme+'upper_elbowPin', 'greater than',
                            ( global_upperDist_MD, 'outputX' ), (upper_add_lower_PM, 'output1D' ),
                            ( global_upperDist_MD, 'outputX' ), ( upper_add_lower_PM, 'output1D' ) )

    lower_elbowPin_condition = conditionNode( nme+'lower_elbowPin', 'greater than',
                            ( global_lowerDist_MD, 'outputX' ), (lower_minus_upper_PM, 'output1D' ),
                            ( global_lowerDist_MD, 'outputX' ), ( lower_minus_upper_PM, 'output1D' ) )

    ###
    # connect it to blend2Attr nodes

    node = cmds.shadingNode('blendTwoAttr', asUtility=True)
    upperBlend2Node = cmds.rename(node, nme+'_upperStretch_blendTwoAttr')
    node = cmds.shadingNode('blendTwoAttr', asUtility=True)
    lowerBlend2Node = cmds.rename(node, nme+'_lowerStretch_blendTwoAttr')
    # connect upper condition to input[0]
    cmds.connectAttr( upper_add_stretchLower_PM+'.output1D' , upperBlend2Node+'.input[0]', f=True )
    cmds.connectAttr( upper_elbowPin_condition+'.outColorR', upperBlend2Node+'.input[1]', f=True )
    cmds.connectAttr( lower_minus_stretchUpper_PM+'.output1D' , lowerBlend2Node+'.input[0]', f=True )
    cmds.connectAttr( lower_elbowPin_condition+'.outColorR', lowerBlend2Node+'.input[1]', f=True )

    # connect blend2Attr to joints translate x
    # check for mirrored joints and fix it
    elbowJntX = cmds.getAttr( elbowJnt+'.translateX' )
    handJntX = cmds.getAttr( handJnt+'.translateX' )
    if elbowJntX < 0:
        elbowMirrorNegativeFix_MD = multiDivideNode( nme+'elbowMirrorNegativeFix', 'multiply',
                        upperBlend2Node, 'output', '', -1 )
        cmds.connectAttr( elbowMirrorNegativeFix_MD+'.outputX', elbowJnt+'.translateX', f=True )
    else:
        cmds.connectAttr( upperBlend2Node+'.output', elbowJnt+'.translateX', f=True )

    if handJntX < 0:
        handMirrorNegativeFix_MD = multiDivideNode( nme+'handMirrorNegativeFix', 'multiply',
                        lowerBlend2Node, 'output', '', -1 )
        cmds.connectAttr( handMirrorNegativeFix_MD+'.outputX', handJnt+'.translateX', f=True )
    else:
        cmds.connectAttr( lowerBlend2Node+'.output', handJnt+'.translateX', f=True )

    print 'addStretchyIKJoints function end here ------------------------'
    return (upperBlend2Node, lowerBlend2Node, checkStretch_condition)

__author__ = 'Jerry'


from rutils.rig_utils import *
from rutils.rig_nodes import *
from rutils.rig_measure import *
from rutils.rig_transform import *
from rutils.rig_anim import *
from make.rig_controls import *
from rutils.rig_modules import *
from rutils.rig_chain import *

import pymel.core as pm
import maya.mel as mm
import maya.cmds as cmds
import string

ABC = list(string.ascii_uppercase)


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


'''

ik fk chain spline for tail

'''

def rig_ikChainSpline( name, rootJnt, ctrlSize=1.0, **kwds ):
	numIkControls = defaultReturn(5, 'numIkControls', param=kwds)
	numFkControls = defaultReturn(5, 'numFkControls', param=kwds)

	parentRoot = defaultReturn('spineJA_JNT', 'parent', param=kwds)

	module = rig_module(name)

	ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
	ctrlSizeQuarter = [ctrlSize / 4.0, ctrlSize / 4.0, ctrlSize / 4.0]
	ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

	chainList = rig_chain(rootJnt).chain

	numJoints = len(chainList)

	ctrlPos = []
	for i in range(0, numJoints):
		if i % 5 == 0:
			ctrlPos.append(chainList[i])

	# make ik driver controls/joints
	fkControls = []
	ikControls = []
	driverJntList = []
	fkScale = 1.5
	for i in range(0, numIkControls):
		driverJnt = rig_transform(0, name=name+'DriverJ' + ABC[i], type='joint',
		                          target=ctrlPos[i], parent=module.parts,
		                          rotateOrder=2).object
		driverJntList.append(driverJnt)

		driverCtrl = rig_control(name=name+'Driver' + ABC[i], shape='box', modify=1, scale=ctrlSizeHalf,
		                         colour='green', parentOffset=module.controlsSec, rotateOrder=2)
		ikControls.append(driverCtrl)
		pm.delete(pm.parentConstraint(driverJnt,driverCtrl.offset))
		pm.parentConstraint(driverCtrl.con, driverJnt, mo=True)

		lockTranslate = []
		ctrlShape = 'circle'
		if i == 0:
			lockTranslate = ['tx', 'ty', 'tz']
			ctrlShape = 'pyramid'
		else:
			lockTranslate = []
		fkCtrl = rig_control(name=name+'FK'+ABC[i], shape=ctrlShape, modify=2,
		                     targetOffset=ctrlPos[i], parentOffset=module.controls,
		                     lockHideAttrs=lockTranslate,
		                     scale=((ctrlSize[0])*fkScale,(ctrlSize[1])*fkScale,(ctrlSize[
				2])*fkScale ))

		if i == 0:
			if pm.objExists(parentRoot):
				pm.parentConstraint(parentRoot, fkCtrl.offset, mo=True)

			if pm.objExists(parentRoot) and pm.objExists('worldSpace_GRP'):
				constrainObject(fkCtrl.modify[0],
				                [fkCtrl.offset, 'worldSpace_GRP'],
				                fkCtrl.ctrl, ['parent', 'world'],
				                type='orientConstraint')

		pm.parentConstraint( fkCtrl.con, driverCtrl.offset, mo=True )

		if i > 0:
			parentOffset = fkControls[i - 1].con
			pm.parent(fkCtrl.offset, parentOffset)

		fkControls.append(fkCtrl)

		fkScale = fkScale - 0.1

	# shape controls
	rootCtrl = fkControls[0]
	pm.addAttr(rootCtrl.ctrl, ln='SHAPE', at='enum',
	           enumName='___________',
	           k=True)
	rootCtrl.ctrl.SHAPE.setLocked(True)
	pm.addAttr(rootCtrl.ctrl, longName='curl', at='float', k=True, min=-10,
	           max=10, dv=0)
	pm.addAttr(rootCtrl.ctrl, longName='curlSide', at='float', k=True, min=-10,
	           max=10, dv=0)
	for i in range(1, numIkControls):
		rig_animDrivenKey(rootCtrl.ctrl.curl, (-10,0, 10),
		                  fkControls[i].modify[0] + '.rotateX', (-90,0, 90 ))
		rig_animDrivenKey(rootCtrl.ctrl.curlSide, (-10, 0, 10),
		                  fkControls[i].modify[0] + '.rotateZ', (-90, 0, 90 ))


	ik = rig_ik(name, rootJnt, chainList[-1], 'ikSplineSolver', numSpans=numIkControls)
	pm.parent(ik.handle, ik.curve, module.parts)

	lowerAim = rig_transform(0, name=name+'LowerAim', type='locator',
	                              parent=module.parts, target=ikControls[1].con).object
	upperAim = rig_transform(0, name=name+'UpperAim', type='locator',
	                              parent=module.parts, target=ikControls[-2].con).object

	pm.rotate(lowerAim, 0, 0, -90, r=True, os=True)
	pm.rotate(upperAim, 0, 0, -90, r=True, os=True)

	pm.parentConstraint(ikControls[1].con, lowerAim, mo=True)
	pm.parentConstraint(ikControls[-2].con, upperAim, mo=True)

	aimTop = mm.eval(
		'rig_makePiston("' + lowerAim + '", "' + upperAim + '", "'+name+'Aim");')

	pm.move( upperAim+'Up', 0, 30, 0,r=True,os=True )
	pm.move(lowerAim + 'Up', 0, 20, 0, r=True, os=True)

	# advanced twist
	pm.setAttr(ik.handle + '.dTwistControlEnable', 1)
	pm.setAttr(ik.handle + '.dWorldUpType', 2)  # object up start and end
	pm.setAttr(ik.handle + '.dForwardAxis', 2)  # positive y
	pm.setAttr(ik.handle + '.dWorldUpAxis', 6)  # positive x

	pm.connectAttr(upperAim+'Up.worldMatrix[0]', ik.handle.dWorldUpMatrixEnd, f=True)
	pm.connectAttr(lowerAim+'Up.worldMatrix[0]', ik.handle.dWorldUpMatrix, f=True)

	pm.parent(aimTop, module.parts)

	pm.select(ik.curve)
	curveShape = pm.pickWalk(direction='down')
	curveInfoNode = pm.arclen(curveShape[0], ch=True)
	curveInfo = pm.rename(curveInfoNode, name + '_splineIk_curveInfo')
	globalCurve = pm.duplicate(ik.curve)
	globalCurve = pm.rename(globalCurve, name + 'global_splineIk_curve')
	pm.select(globalCurve)
	globalCurveShape = pm.pickWalk(direction='down')
	globalCurveInfoNode = pm.arclen(globalCurveShape[0], ch=True)
	globalCurveInfo = pm.rename(globalCurveInfoNode, name + 'global_splineIk_curveInfo')
	pm.parent(globalCurve, module.parts)
	pm.setAttr(globalCurve + '.inheritsTransform', 1)

	distanceToStretch_PM = plusMinusNode(name + '_distanceToStretch', 'subtract',
	                                     curveInfo, 'arcLength', globalCurveInfo, 'arcLength')

	correctAdd_Minus_MD = multiplyDivideNode(name + '_correctAdd_Minus', 'multiply',
	                                         input1=[-1, 0, 0],
	                                         input2=[distanceToStretch_PM + '.output1D', 0, 0],
	                                         output=[])

	toggleStretch_ctrl_MD = multiplyDivideNode(name + '_toggleStretch_ctrl', 'multiply',
	                                           input1=[0, 0, 0],
	                                           input2=[correctAdd_Minus_MD + '.outputX', 0, 0],
	                                           output=[])

	distanceStretchCurve_PM = plusMinusNode(name + '_distanceStretchCurve', 'sum',
	                                        curveInfo, 'arcLength', toggleStretch_ctrl_MD,
	                                        'outputX')

	globalCurveStretchyFix_MD = multiplyDivideNode(name + '_globalCurveStretchyFix', 'divide',
	                                               input1=[distanceStretchCurve_PM + '.output1D', 0,

	                                                       0],
	                                               input2=[globalCurveInfo + '.arcLength', 1, 1],
	                                               output=[])

	pm.addAttr(fkControls[0].ctrl, longName='stretch', shortName='ts',
	           attributeType="double",
	           min=0, max=1, defaultValue=0, keyable=True)

	connectReverse(input=(fkControls[0].ctrl + '.stretch', 0, 0),
	               output=(toggleStretch_ctrl_MD + '.input1X', 0, 0))

	for i in range(0, len(chainList) - 1):
		pm.connectAttr(globalCurveStretchyFix_MD + '.outputX', chainList[i] + '.scaleY',
		               f=True)

	pm.skinCluster(driverJntList, ik.curve, tsb=True)
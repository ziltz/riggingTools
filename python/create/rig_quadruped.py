__author__ = 'Jerry'


from make.rig_ik import *
from make.rig_controls import *

from rutils.rig_chain import *
from rutils.rig_nodes import *
from rutils.rig_math import *
from rutils.rig_modules import rig_module
from rutils.rig_transform import rig_transform
from rutils.rig_curve import *
from rutils.rig_joint import *

import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mm
import string

ABC = list(string.ascii_uppercase)



class rig_quadruped(object):

    def __init__(self, **kwds):

        self.globalCtrl = pm.PyNode('global_CTRL')

        self.switchLoc = 'ikFkSwitch_LOC'

        self.clavicleName = 'clavicleJA_JNT'
        self.scapulaName = 'scapulaJA_JNT'

        '''
        self.armName = 'armJA_JNT'
        self.elbowName = 'elbowJA_JNT'
        self.handName = 'handJA_JNT'
        self.handFngName = 'handJB_JNT'
        '''
        self.armName = 'armJA_JNT'
        self.elbowName = 'elbowJA_JNT'
        self.handName = 'handJA_JNT'
        self.handBName = 'handJB_JNT'
        self.fngName = 'knuckleJA_JNT'

        self.fngThumb = 'fngThumbJA_JNT'
        self.fngIndex = 'fngIndJA_JNT'
        self.fngMid = 'fngMidJA_JNT'
        self.fngRing = 'fngRingJA_JNT'
        self.fngPinky = 'fngPnkyJA_JNT'

        self.legName = 'legJA_JNT'
        self.kneeName = 'kneeJA_JNT'
        self.footName = 'footJA_JNT'
        self.footBName = 'footJB_JNT'
        self.toesName = 'toesJA_JNT'

        self.toeThumb = 'toeThumbJA_JNT'
        self.toeIndex = 'toeIndJA_JNT'
        self.toeMid = 'toeMidJA_JNT'
        self.toeRing = 'toeRingJA_JNT'
        self.toePinky = 'toePnkyJA_JNT'

        self.elbowAxis = 'rx'
        self.kneeAxis = 'rz'

        self.armJoints = []
        self.legJoints = []

        # values : poleVector, hand, fk, fingers
        self.armControls = {}
        self.armTop = ''
        self.shoulderControl = None

        # values : poleVector, foot, fk, toes
        self.legControls = {}
        self.legTop = ''
        self.pelvisControl = None

        self.spineFullBodyCtrl = None
        self.spineUpperCtrl = None
        self.spineLowerCtrl = None

        self.spineConnection = 'spineJF_JNT'
        self.centerConnection = 'spineJA_JNT'
        self.pelvisConnection = 'pelvisJA_JNT'

        self.spineModule = ''
        self.neckModule = ''
        self.headModule = ''
        
        self.shoulderModule = ''
        self.armModule = ''
        self.legModule = ''

        self.quadShoulderBaseLimit = 15
        self.scapulaBaseLimit = 15

    def create(self):

        self.spine()

        self.neck()

        self.head()

        for s in ['l', 'r']:
            self.shoulder(s)
            self.arm(s)
            self.leg(s)

        self.pelvis()


        return


    '''
    chains[0] = result
    chains[1] = ik
    chains[2] = fk
    '''
    def connectIkFkSwitch(self, chains, module, name='rigSwitch' ):
        # switch

        switchParent = module.parts
        if pm.objExists('rig_GRP'):
            switchParent = 'rig_GRP'

        if not pm.objExists(self.switchLoc):
            self.switchLoc = pm.PyNode(rig_transform(0, type='locator',
                                                 name='ikFkSwitch',
                                           parent=switchParent).object)

        pm.addAttr(self.switchLoc, longName=name, at='float', k=True, min=0,
                   max=1)

        # blend joints together

        for i in range(0, len(chains[0])):

            con = pm.orientConstraint( chains[1][i], chains[2][i], chains[0][i] )
            targetsOrient = con.getWeightAliasList()
            pm.setAttr(con.interpType, 2)

            con = pm.pointConstraint(chains[1][i], chains[2][i], chains[0][i])
            targetsPoint = con.getWeightAliasList()

            pm.connectAttr( self.switchLoc+'.'+name, targetsOrient[0] )
            pm.connectAttr(self.switchLoc + '.' + name, targetsPoint[0])
            connectReverse(input=(self.switchLoc+'.'+name, self.switchLoc+'.'+name, 0),
                           output=(targetsOrient[1], targetsPoint[1], 0))

            '''
            blendColors(chains[1][i], chains[2][i], chains[0][i], name=name+str(i),
                        driverAttr=self.switchLoc+'.'+name,
                        attribute='rotate')

            blendColors(chains[1][i], chains[2][i], chains[0][i], name=name + str(i),
                        driverAttr=self.switchLoc + '.' + name,
                        attribute='translate')
            '''

        switchAttr = getattr(self.switchLoc, name)
        pm.connectAttr( switchAttr, module.top.ikFkSwitch  )



    def spine(self,  ctrlSize=1 ):
        name = 'spine'

        module = rig_module(name)
        self.spineModule = module

        pm.parent(self.centerConnection, module.skeleton)

        ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
        ctrlSizeQuarter = [ctrlSize / 4.0, ctrlSize / 4.0, ctrlSize / 4.0]
        ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

        '''
        string $spline = cMS_makeSpline($baseName, $nControls, $controlType, $detail, $nRead, $readType, $ctrls, $reads, $bConstrainMid) ;
    string $spline = cMS_makeSpline($baseName, $nControls, $controlType, 8, 0, "null", $ctrls, $reads, 1) ;

        '''

        # full body control
        spineFullBody = rig_control(name='spineFullBody', shape='box', modify=1,
                                    scale=ctrlSize,
                                 colour='yellow', parentOffset=module.controls, rotateOrder=2)
        pm.delete(pm.pointConstraint( 'spineJA_JNT', spineFullBody.offset ))
        self.spineFullBodyCtrl = spineFullBody
        spineTop = pm.xform('spineJF_JNT', translation=True, query=True, ws=True)
        spineBot = pm.xform('spineJA_JNT', translation=True, query=True, ws=True)
        spineDistance = lengthVector(spineBot, spineTop)
        pm.scale(pm.PyNode(spineFullBody.ctrl+'.cv[:]'), 0.5, 1, 0.5)
        pm.rotate( pm.PyNode(spineFullBody.ctrl+'.cv[:]') , 90, 0,0,r=True,os=True )

        pm.move(pm.PyNode( spineFullBody.ctrl+'.cv[:]' ), [0, spineDistance/1.5, 0],
                relative=True,
                worldSpace=True)
        spineFullBody.gimbal = createCtrlGimbal(spineFullBody)
        spineFullBody.pivot = createCtrlPivot(spineFullBody)


        

        # spine lower
        spineLower = rig_control(name='spineLower', shape='box', modify=1,
                                 targetOffset='spineJB_JNT',
                                 constrainOffset=spineFullBody.con, scale=ctrlSize,
                                 colour='yellow', parentOffset=module.controls, rotateOrder=2)
        spineLower.gimbal = createCtrlGimbal(spineLower)
        spineLower.pivot = createCtrlPivot(spineLower)

        self.spineLowerCtrl = spineLower

        constrainObject(spineLower.modify,
                        [spineLower.offset, 'worldSpace_GRP'],
                        spineLower.ctrl, ['fullBody', 'world'],
                        type='parentConstraint')

        pm.parentConstraint( spineLower.con, self.centerConnection, mo=True )

        pm.move(pm.PyNode(spineLower.ctrl + '.cv[:]'),
                [0, 0, 0.5],
                relative=True,
                worldSpace=True)
        pm.scale(pm.PyNode(spineLower.ctrl + '.cv[:]'), 1, 0.7, 1)

        # spine upper
        spineUpper = rig_control(name='spineUpper', shape='box', modify=1,scale=ctrlSize,
                                 colour='yellow', parentOffset=module.controls, rotateOrder=2)
        spineUpper.gimbal = createCtrlGimbal(spineUpper)
        spineUpper.pivot = createCtrlPivot(spineUpper)

        self.spineUpperCtrl = spineUpper

        pm.delete(pm.parentConstraint( 'spineJE_JNT', spineUpper.offset ))
        pm.parentConstraint( spineFullBody.con, spineUpper.offset, mo=True )

        pm.move(pm.PyNode(spineUpper.ctrl + '.cv[:]'),
                [0, 0, 1.5],
                relative=True,
                worldSpace=True)

        constrainObject(spineUpper.modify,
                        [spineUpper.offset, 'worldSpace_GRP'],
                        spineUpper.ctrl, ['fullBody', 'world'],
                        type='parentConstraint')

        pm.addAttr(spineUpper.ctrl, ln='MOTION', at='enum',
                   enumName='___________',
                   k=True)
        spineUpper.ctrl.MOTION.setLocked(True)

        # duplicate chain

        splineJoints = rig_jointCopyChain('spineJB_JNT', replaceName=('spine','spineSpline') )

        spineChain = rig_chain(self.centerConnection).chainChildren

        driverJntsList = []
        driverCtrlList = {}
        for i in range (0, len(spineChain)):
            driverJnt = rig_transform(0, name='spineDriverJ'+ABC[i+1], type='joint',
                                      target=spineChain[i], parent=module.parts,
                                      rotateOrder=2).object
            driverJntsList.append(driverJnt)

            driverCtrl = rig_control(name='spineDriver'+ABC[i+1], shape='box', modify=1,
                                    targetOffset=spineChain[i], scale=ctrlSizeHalf,
                                    colour='green', parentOffset=module.controlsSec, rotateOrder=2)
            driverCtrlList[ 'spine'+ABC[i+1] ] = driverCtrl

            pm.parentConstraint( driverCtrl.con, driverJnt, mo=True )

            pm.scale(driverCtrl.ctrl.cv, 1, 0.2, 1, os=True, r=True)
            pm.scale(driverCtrl.ctrl.cv, 1.5, 1, 1.5, os=True, r=True)

            drivenOffset = rig_transform(0, name='spineDriven'+ABC[i+1]+'Offset',
                                      target=spineChain[i], parent=module.parts,
                                      rotateOrder=2).object
            drivenCon = rig_transform(0, name='spineDriven'+ABC[i+1]+'Con',
                                      target=spineChain[i], parent=drivenOffset,
                                      rotateOrder=2).object
            pm.parentConstraint( splineJoints[i], drivenOffset, mo=True )
            pm.parentConstraint( drivenCon, spineChain[i], mo=True )
            for at in ( 'rx','ry','rz' ):
                attr = getattr( driverCtrl.ctrl, at)
                pm.connectAttr( attr, drivenCon+'.'+at )

        pm.hide('spineDriverBOffset_GRP')

        # constrain control drivers
        #pm.parentConstraint( spineUpper.con, driverCtrlList['spineE'].offset, mo=True )
        con = pm.parentConstraint(spineUpper.con,spineLower.con, driverCtrlList['spineE'].offset, mo=True)
        pm.parentConstraint( spineUpper.con, driverCtrlList['spineF'].offset, mo=True )

        pm.parentConstraint(spineLower.con, driverCtrlList['spineB'].offset, mo=True)
        pm.parentConstraint(spineLower.con, driverCtrlList['spineC'].offset, mo=True)
        pm.parentConstraint(spineUpper.con,spineLower.con, driverCtrlList['spineD'].offset, mo=True)

        # set spineE 
        pm.setAttr(con.interpType, 2 )
        targets = con.getWeightAliasList()
        pm.setAttr( targets[1], 0.5 )

        # create spline ik
        #ik = rig_ik(name, 'spineJB_JNT', 'spineJF_JNT', 'ikSplineSolver', numSpans=5)
        ik = rig_ik(name, 'spineSplineJB_JNT', 'spineSplineJF_JNT', 'ikSplineSolver', numSpans=5)
        pm.parent(ik.handle, ik.curve, module.parts)
        #// Result: [u'spine2_ik_Handle', u'effector6', u'curve2'] //

        spineLowerAim = rig_transform(0, name='spineLowerAim', type='locator',
                                parent=module.parts, target='spineJB_JNT' ).object
        spineUpperAim = rig_transform(0, name= 'spineUpperAim', type='locator',
                                    parent=module.parts, target='spineJE_JNT').object

        #pm.setAttr(spineLowerAim + '.rotateZ', -90)
        #pm.setAttr(spineUpperAim + '.rotateZ', -90)
        pm.rotate( spineLowerAim, 0,0,-90, r=True , os=True)
        pm.rotate(spineUpperAim, 0, 0, -90, r=True, os=True)

        pm.parentConstraint(spineLower.con, spineLowerAim, mo=True)
        pm.parentConstraint(spineUpper.con, spineUpperAim, mo=True)

        spineAimTop = mm.eval(
            'rig_makePiston("' + spineLowerAim + '", "' + spineUpperAim + '", "spineAim");')

        pm.setAttr("spineUpperAim_LOCUp.translateY", 10000)
        pm.setAttr( "spineLowerAim_LOCUp.translateY", 10000)

        # advanced twist spine
        pm.setAttr(ik.handle + '.dTwistControlEnable', 1)
        pm.setAttr(ik.handle + '.dWorldUpType', 2)  # object up start and end
        pm.setAttr(ik.handle + '.dForwardAxis', 2)  # positive y
        pm.setAttr(ik.handle + '.dWorldUpAxis', 8)  # closest x

        pm.connectAttr('spineUpperAim_LOCUp.worldMatrix[0]', ik.handle.dWorldUpMatrixEnd, f=True)
        pm.connectAttr('spineLowerAim_LOCUp.worldMatrix[0]', ik.handle.dWorldUpMatrix, f=True)

        pm.parent(spineAimTop, module.parts)

        axis = '.ry'
        # create new attributes
        pm.addAttr(spineUpper.ctrl, ln="autoTwist", at="double", dv=0, min=0, max=1, k=False)
        pm.addAttr(spineUpper.ctrl, ln="twistOffset", at="double", dv=0, k=True)

        # create nodes for autoTwist and twistOffset
        autoTwist1 = pm.createNode("multiplyDivide", n="md_" + spineUpper.ctrl + "_autoTwist1")
        autoTwist2 = pm.createNode("multiplyDivide", n="md_" + spineUpper.ctrl + "_autoTwist2")
        twistOffset1 = pm.createNode("plusMinusAverage", n="pma_" + spineUpper.ctrl + "_twistOffset1")
        twistOffset2 = pm.createNode("plusMinusAverage", n="pma_" + spineUpper.ctrl + "_twistOffset2")

        # connect the end control
        pm.connectAttr(spineUpper.ctrl + axis, autoTwist1 + ".input1X")
        pm.connectAttr(spineUpper.ctrl + ".autoTwist", autoTwist1 + ".input2X")

        pm.connectAttr(autoTwist1 + ".outputX", twistOffset1 + ".input1D[0]")
        pm.connectAttr(spineUpper.ctrl + ".twistOffset", twistOffset1 + ".input1D[1]")

        # connect the start control
        pm.connectAttr(spineLower.ctrl + axis, autoTwist2 + ".input1X")
        pm.connectAttr(spineUpper.ctrl + ".autoTwist", autoTwist2 + ".input2X")

        pm.connectAttr(twistOffset1 + ".output1D", twistOffset2 + ".input1D[0]")
        pm.connectAttr(autoTwist2 + ".outputX", twistOffset2 + ".input1D[1]")

        pm.setAttr(twistOffset2 + ".operation", 2)  # subtract

        # connect to the ikHandle
        #pm.connectAttr(spineLower.ctrl + axis, ik.handle + ".roll")
        pm.connectAttr(twistOffset2 + ".output1D", ik.handle + ".twist")

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


        correctAdd_Minus_MD = multiplyDivideNode(name+'_correctAdd_Minus', 'multiply',
                                                 input1=[-1, 0, 0],
                                                 input2=[distanceToStretch_PM+'.output1D', 0, 0],
                                                 output=[])

        toggleStretch_ctrl_MD = multiplyDivideNode(name + '_toggleStretch_ctrl', 'multiply',
                                                 input1=[0, 0, 0],
                                                 input2=[correctAdd_Minus_MD + '.outputX', 0, 0],
                                                 output=[])

        distanceStretchCurve_PM = plusMinusNode(name + '_distanceStretchCurve', 'sum',
                                                curveInfo, 'arcLength', toggleStretch_ctrl_MD,
                                                'outputX')

        globalCurveStretchyFix_MD = multiplyDivideNode(name + '_globalCurveStretchyFix', 'divide',
                                                 input1=[distanceStretchCurve_PM+'.output1D', 0, 0],
                                                 input2=[globalCurveInfo + '.arcLength', 1, 1],
                                                 output=[])

        pm.addAttr(spineUpper.ctrl, longName='stretch', shortName='ts',
                     attributeType="double",
                     min=0, max=1, defaultValue=0.5, keyable=True)

        connectReverse(input=(spineUpper.ctrl + '.stretch', 0, 0),
                       output=(toggleStretch_ctrl_MD + '.input1X', 0, 0))

        for i in range(0, len(splineJoints)-1 ):
            pm.connectAttr(globalCurveStretchyFix_MD + '.outputX', splineJoints[i] + '.scaleY',
                           f=True)

        pm.skinCluster(driverJntsList, ik.curve, tsb=True)

        cmds.dgdirty(allPlugs=True)
        cmds.refresh()

        return module

    def neck (self, ctrlSize, splinePosList=[], **kwds):
        name = 'neck'
        rootJoint = 'neckJA_JNT'
        endJoint = 'neckJEnd_JNT'
        fkStartNeck = 'neckFKACon_GRP'
        parent = 'spineJF_JNT'
        parentName = 'spine'
        spine = 'spineUpperCon_GRP'
        fullBody = 'spineFullBodyCon_GRP'
        numCons = defaultReturn(10,'numControls', param=kwds)
        numIKCtrls = numCons
        numFKCtrls = numCons
        worldSpace = 'worldSpace_GRP'
        dWorldUpAxis = 6 # positive x

        ctrlDouble = [ctrlSize*2, ctrlSize*2, ctrlSize*2]
        ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
        ctrlSizeQuarter = [ctrlSize / 4.0, ctrlSize / 4.0, ctrlSize / 4.0]
        ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

        listOrigJoints = cmds.listRelatives(rootJoint, type="joint", ad=True)
        listOrigJoints.append(rootJoint)
        listOrigJoints.reverse()

        listJoints = rig_jointCopyChain(rootJoint, replaceName=('neck','neckSpline') )
        
        rootJoint = 'neckSplineJA_JNT'
        endJoint = 'neckSplineJEnd_JNT'

        '''
        rig_makeSpline(string $baseName, int $nControls, string $controlType, int $detail,
                        int $nRead, string $readType, string $ctrls[], string $reads[], int $bConstrainMid
            )
        '''
        # make cMus tail joints
        mm.eval(
            'string $ctrls[];string $reads[];rig_makeSpline( "'+name+'", 4, "cube", 8, '+str(numIKCtrls)+', "joint", $ctrls, $reads, 0);')

        # place them every thirds
        if len(splinePosList) == 0:
            thirds = len(listJoints)/3
            pm.delete(pm.parentConstraint( rootJoint, name+'BaseIKOffset_GRP' ))
            pm.delete(pm.parentConstraint( listJoints[thirds], name+'MidAIKOffset_GRP' ))
            pm.delete(pm.parentConstraint( listJoints[thirds+thirds], name+'MidBIKOffset_GRP' ))
            pm.delete(pm.parentConstraint( listJoints[len(listJoints)-2], name+'TipIKOffset_GRP' ))
        elif len(splinePosList) > 0:
            pm.delete(pm.parentConstraint( splinePosList[0], name+'BaseIKOffset_GRP' ))
            pm.delete(pm.parentConstraint( splinePosList[1], name+'MidAIKOffset_GRP' ))
            pm.delete(pm.parentConstraint( splinePosList[2], name+'MidBIKOffset_GRP' ))
            pm.delete(pm.parentConstraint( splinePosList[3], name+'TipIKOffset_GRP' ))

        neckModule = rig_ikChainSpline( name , rootJoint, ctrlSize=ctrlSize[0], parent=parent,
                                       numIkControls=numIKCtrls, numFkControls=numFKCtrls, dWorldUpAxis= dWorldUpAxis)

        self.neckModule = neckModule

        # make aim
        #headProxy = rig_transform(0, name='headProxy', type='locator',
        #                        parent=neckModule.parts, target='neckJEnd_JNT').object

        headNeckControl = rig_control(name='headNeck', shape='pyramid', modify=2,
                                    colour='white', parentOffset=neckModule.controls, rotateOrder=2, scale=ctrlDouble)
        pm.delete(pm.parentConstraint( endJoint, headNeckControl.offset ))
        constrainObject(headNeckControl.offset,
                        [ fkStartNeck , parent, fullBody, 'worldSpace_GRP'],
                        headNeckControl.ctrl, [ 'neckBase','spineUpper', 'fullBody', 'world'],
                        type='parentConstraint', spaceAttr='space')
        constrainObject(headNeckControl.modify[0],
                        ['worldSpace_GRP' , parent, fullBody],
                        headNeckControl.ctrl, [ 'world', 'spineUpper', 'fullBody'],
                        type='orientConstraint',spaceAttr='orientSpace')

        headPos = pm.xform('headJA_JNT', translation=True, query=True, ws=True)
        headEndPos = pm.xform( 'headJEnd_JNT', translation=True, query=True, ws=True)
        headLength = lengthVector(headPos, headEndPos)
        pm.move(pm.PyNode(headNeckControl.ctrl + '.cv[:]'), 0, headLength/3, 0, r=True,
                os=True)

        aimPointerBase = rig_transform(0, name=name+'PointerBase', type='locator',
                                parent=neckModule.parts, target=parent).object
        aimPointerTip = rig_transform(0, name=name+'PointerTip', type='locator',
                                parent=neckModule.parts, target=endJoint).object

        pm.rotate(aimPointerBase, 0, 0, -90, r=True, os=True)
        pm.rotate(aimPointerTip, 0, 0, -90, r=True, os=True)

        pm.parentConstraint(parent, aimPointerBase, mo=True)
        pm.parentConstraint(headNeckControl.con, aimPointerTip, mo=True)

        aimPointerTop = mm.eval(
            'rig_makePiston("' + aimPointerBase + '", "' + aimPointerTip + '", "'+name+'PointerAim");')


        # neck upgrade
        neckJnts = pm.listRelatives( name+'SplineJoints_GRP', type='joint')
        for i in range (1, len(neckJnts)):
            neckNme = neckJnts[i].stripNamespace()
            neckIK = neckJnts[i]
            neckFK = neckNme.replace('IK', 'FK')
            neckFK = neckFK.replace('_JNT', '')

            constrainObject(neckFK+'Modify2_GRP',
                            [neckFK+'Modify1_GRP',neckIK ],
                            'neckFKA_CTRL', ['FK','IK'], type='parentConstraint', spaceAttr='neckSpace')


        # neck focus aim 
        neckPos = pm.xform(rootJoint, translation=True, query=True, ws=True)
        headEndPos = pm.xform( 'headJEnd_JNT', translation=True, query=True, ws=True)
        neckLength = lengthVector(neckPos, headEndPos)

        neckFocusBase = rig_transform(0, name=name+'FocusBase', type='locator',
                                parent=neckModule.parts, target=rootJoint).object
        neckFocusTip = rig_transform(0, name=name+'FocusTip', type='locator',
                                parent=neckModule.parts, target=rootJoint).object

        pm.rotate(neckFocusBase, 0, 0, -90, r=True, os=True)
        pm.rotate(neckFocusTip, 0, 0, -90, r=True, os=True)

        pm.move(neckFocusTip, -1.5*neckLength, 0, -1*neckLength/4, os=True, r=True, wd=True  )

        pm.parentConstraint(parent, neckFocusBase, mo=True)
        #pm.parentConstraint(headNeckControl.con, aimPointerTip, mo=True)
        neckFocusControl = rig_control(name='neckFocus', shape='sphere', modify=1, lockHideAttrs=['rx','ry','rz'],
                                    colour='white', parentOffset=neckModule.controls, rotateOrder=2, scale=ctrlSizeHalf)

        pm.delete(pm.parentConstraint( neckFocusTip, neckFocusControl.offset))
        pm.rotate(neckFocusControl.offset, 0, 0, 90, r=True, os=True)
        pm.parentConstraint(neckFocusControl.con, neckFocusTip, mo=True)


        constrainObject(neckFocusControl.offset,
                    [ 'spineFullBodyCon_GRP', 'spineLowerCon_GRP','worldSpace_GRP'],
                    neckFocusControl.ctrl, [ 'fullBody', 'spineLower', 'world'], type='parentConstraint')

        #aimConstraint -mo -weight 1 -aimVector 0 -1 0 -upVector 1 0 0 -worldUpType "objectrotation" -worldUpVector 1 0 0 -worldUpObject locator1;

        neckFocusUp = rig_transform(0, name=name+'FocusBaseUp', type='locator',
                                parent=parent, target=parent).object
        pm.move(neckFocusUp, 0, 100, 0, ws=True, r=True  )
        pm.hide(neckFocusUp)
        pm.aimConstraint( parent, neckFocusControl.con, mo=True, w=1, aimVector=(0,-1,0), upVector=(1,0,0),
                              worldUpType='objectrotation', worldUpVector=(1,0,0), worldUpObject=neckFocusUp )

        headFocusOffset = rig_transform(0, name='headFocusOffset', type='group',
                                parent=neckModule.parts, target=headNeckControl.ctrl).object
        headFocusLoc = rig_transform(0, name='headFocus', type='locator',
                                parent=headFocusOffset, target=headFocusOffset).object
        pm.parentConstraint(headNeckControl.modify[0], headFocusOffset, mo=True)
        headFocusUp = rig_transform(0, name='headFocusUp', type='locator',
                                parent=neckFocusControl.ctrl, target=neckFocusControl.ctrl).object
        pm.hide(headFocusUp)
        pm.move(headFocusUp, 0, 0, -100, os=True, r=True  )
        pm.aimConstraint( neckFocusControl.ctrl, headFocusLoc, mo=True, w=1, aimVector=(0,1,0), upVector=(1,0,0),
                             worldUpType='objectrotation', worldUpVector=(0,0,-1), worldUpObject=headFocusUp )

        constrainObject(headNeckControl.modify[1],
                    [headNeckControl.modify[0],headFocusLoc ],
                    neckFocusControl.ctrl, [], type='orientConstraint', interp=2,
                    doBlend=1, doSpace=0, spaceAttr='focusHead',blendVal=1)

        #aimConstraint -mo -weight 1 -aimVector 0 1 0 -upVector 1 0 0 -worldUpType "object" -worldUpObject neckFocusUp_LOC;


        neckFocusTop = mm.eval(
            'rig_makePiston("' + neckFocusBase + '", "' + neckFocusTip + '", "'+name+'Focus");')

        rig_curveBetweenTwoPoints('neckFKA_CTRL', neckFocusControl.con,name='neckBase')
        rig_curveBetweenTwoPoints(headNeckControl.con, neckFocusControl.con, name='headNeck')

        #pm.delete('neckFKAModify1_GRP_orientConstraint1')
        #pm.deleteAttr( 'neckFKA_CTRL', at='space' )
        constrainObject('neckFKAModify2_GRP',
                    ['neckFKAOffset_GRP',neckFocusBase ],
                    neckFocusControl.ctrl, [], type='orientConstraint', interp=2,
                    doBlend=1, doSpace=0, spaceAttr='focusNeck',blendVal=1)

        pm.parentConstraint( parent, name+'BaseIKOffset_GRP', mo=True )
        constrainObject(  name+'BaseIKModify_GRP',
                [name+'BaseIKOffset_GRP',aimPointerBase], '', [],
                 type='orientConstraint', doSpace=0, skip=('y','z'), interp=2)

        constrainObject(  name+'MidAIKOffset_GRP',
                [name+'TipIKCon_GRP',name+'BaseIKCon_GRP'], '', [],
                 type='parentConstraint', doSpace=0, setVal=(0.5, 1))
        constrainObject(  name+'MidAIKModify_GRP',
                [aimPointerBase,aimPointerTip], '', [],
                 type='parentConstraint', doSpace=0, skipTrans=('x','z'), skipRot=('y'), interp=2)

        pm.parentConstraint( name+'TipIKCon_GRP', name+'MidBIKOffset_GRP', mo=True )
        constrainObject(name+'MidBIKModify_GRP',
                        [aimPointerBase, aimPointerTip], '', [],
                        type='parentConstraint', doSpace=0, skipTrans=('x','z'), skipRot=('y'), interp=2 )

        pm.parentConstraint( headNeckControl.con, name+'TipIKOffset_GRP', mo=True )
        constrainObject(  name+'TipIKModify_GRP',
                [name+'TipIKOffset_GRP',aimPointerTip], '', [],
                 type='orientConstraint', doSpace=0, skip=('y','z'), interp=2)


        # scale ctrls
        for ctrl in (name+'MidAIK_CTRL', name+'MidBIK_CTRL', name+'TipIK_CTRL'):
            c = pm.PyNode( ctrl )
            pm.scale(c.cv, ctrlSize[0], ctrlSize[0], ctrlSize[0] )
            pm.move(c.cv, [0, 2*ctrlSize[0], 0], relative=True, worldSpace=True)



        #pm.orientConstraint( aimPointerBase.replace('LOC','JNT'), name+'FKAModify2_GRP', mo=True )

        pm.parent(name+'MidAIKOffset_GRP', name+'MidBIKOffset_GRP',
                  neckModule.controls)
        pm.parent(neckJnts, neckModule.skeleton)
        pm.parent(name+'_cMUS',name+'BaseIKOffset_GRP',name+'TipIKOffset_GRP',aimPointerTop,neckFocusTop,neckModule.parts)
        pm.parent(name+'SplineSetup_GRP',name+'BaseIKOffset_GRP',aimPointerTop, neckModule.parts)

        pm.setAttr( neckModule.skeleton+'.inheritsTransform', 0 )

        pm.setAttr("neckFKBOffset_GRP.visibility", 0)

        pm.setAttr("neckFKA_CTRL.stretch", 1 )
        pm.setAttr("neckFKA_CTRL.neckSpace", 1)

        pm.parent( 'neckJA_JNT', 'spineSkeleton_GRP' )
        pm.parent( 'neckSplineJA_JNT', 'spineSkeleton_GRP' )

        # make fk rider 

        neckFKACtrl = pm.PyNode('neckFKA_CTRL')
        for at in ('curl', 'curlSide', 'neckSpace' ):
            neckFKACtrl.attr(at).setKeyable(False)
            neckFKACtrl.attr(at).setLocked(True)


        chainNeck = rig_chain( 'neckJA_JNT' )

        neckChildren = chainNeck.chain

        neckChildren.pop(len(neckChildren)-1)
        neckChildren.pop(0)

        print 'neckChildren'+str(neckChildren)
        #pm.error()
        
        sc = simpleControls(neckChildren,
               modify=1, scale=(40,1,40),directCon=1,parentCon=1,colour='green' )

        offsetFKList = []
        conFKList = []
        j = 1
        for jnt in listOrigJoints:
            if j < len(listOrigJoints):
                offset = rig_transform(0, name= jnt.replace('_JNT','FKOffset'),
                                      target=jnt, parent='spineSkeleton_GRP').object
                pm.parentConstraint( listJoints[j-1], offset, mo=True )

                offsetName = listOrigJoints[j].replace('_JNT','Offset')

                modFK = rig_transform(0, name= offsetName+'Mod',
                                      target=listOrigJoints[j], parent=offset).object
                conFK = rig_transform(0, name= offsetName+'Con',
                                      target=listOrigJoints[j], parent=modFK).object

                offsetFKList.append(offset)
                conFKList.append(conFK)
                j+=1

        for i in range(0, len(offsetFKList)-1):
            pm.parentConstraint(offsetFKList[i+1], conFKList[i], mo=True)

        pm.parentConstraint(headNeckControl.con, conFKList[len(conFKList)-1], mo=True)

        '''
        j = 0
        for jnt in sc:
            control = sc[jnt]
            for at in ['tx','ty','tz','rx','ry','rz']:
                pm.connectAttr( conFKList[j]+'.'+at, control.modify+'.'+at )
            pm.parent( neckChildren[j], control.con )
            j += 1
        '''

        j = 0
        for jnt in neckChildren:
            control = sc[jnt]
            for at in ['tx','ty','tz','rx','ry','rz']:
                pm.connectAttr( conFKList[j]+'.'+at, control.modify+'.'+at )
            pm.parent( jnt, control.con )
            pm.setAttr(jnt+'.v', 0)

            pm.move(control.ctrl + '.cv[:]', 0, 0, -10, r=True,
                os=True)

            pm.select( control.ctrl+'.cv[1:2]' )
            pm.select( control.ctrl+'.cv[6:7]', add=True )
            pm.select( control.ctrl+'.cv[12:15]', add=True )

            cmds.scale ( .5, 1, 1, r=True,scaleX=True )

            j += 1

        pm.parent('neckJA_JNT',offsetFKList[0] )

        offsetEnd = rig_transform(0, name= 'neckJEnd_JNTOffset',
                                      target='neckJEnd_JNT', parent='neckJHCon_GRP').object
        modEnd = rig_transform(0, name= 'neckJEnd_JNTModify',
                                      target='neckJEnd_JNT', parent=offsetEnd).object
        pm.parent('neckJEnd_JNT', modEnd)
        for at in ['tx','ty','tz','rx','ry','rz']:
            pm.connectAttr( conFKList[len(conFKList)-1]+'.'+at, modEnd+'.'+at )

        pm.parentConstraint('neckJA_JNT', 'neckJBOffset_GRP',mo=True)
        pm.setAttr('neckJA_JNT.v', 0)
        pm.setAttr('neckJEnd_JNT.v', 0)
        
        pm.parent('neckJBOffset_GRP', 'neckControls_GRP')

        return neckModule

    def head (self, ctrlSize=1.0):
        name = 'head'

        module = rig_module(name)
        self.headModule = module

        pm.parent('headJA_JNT', module.skeleton)

        ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
        ctrlSizeQuarter = [ctrlSize / 4.0, ctrlSize / 4.0, ctrlSize / 4.0]
        ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

        headControl = rig_control(name='head', shape='box', modify=1, lockHideAttrs=['tx','ty','tz'],
                                  targetOffset='headJA_JNT', scale=ctrlSize,
                                  colour='yellow', parentOffset=module.controls, rotateOrder=2)
        headControl.gimbal = createCtrlGimbal(headControl)
        headControl.pivot = createCtrlPivot(headControl)

        constrainObject(headControl.offset,
                        [ 'neckJEnd_JNT' , 'spineJF_JNT', self.spineFullBodyCtrl.con, 'worldSpace_GRP'],
                        headControl.ctrl, ['neck', 'spineUpper', 'fullBody', 'world'],
                        type='parentConstraint', spaceAttr='space')
        '''
        constrainObject(headControl.modify,
                        ['headNeckCon_GRP', 'neckJEnd_JNT' , 'spineJF_JNT', 'worldSpace_GRP'],
                        headControl.ctrl, ['headNeck','neck', 'spineUpper', 'world'],
                        type='orientConstraint',spaceAttr='orientSpace')
        '''

        headPos = pm.xform('headJA_JNT', translation=True, query=True, ws=True)
        headEndPos = pm.xform( 'headJEnd_JNT', translation=True, query=True, ws=True)
        headLength = lengthVector(headPos, headEndPos)
        pm.move(pm.PyNode(headControl.ctrl + '.cv[:]'), 0, headLength/2, 0, r=True,
                os=True)
        pm.scale(pm.PyNode(headControl.ctrl + '.cv[:]'), 1, 0.5,1, r=True,
                os=True)

        #pm.pointConstraint( 'neckJEnd_JNT', 'headJA_JNT', mo=True )
        #pm.orientConstraint( headControl.con, 'headJA_JNT', mo=True )

        pm.parentConstraint( headControl.con, 'headJA_JNT', mo=True )

        #headControl.ctrl.attr('orientSpace').setKeyable(False)
        #headControl.ctrl.attr('orientSpace').setLocked(True)

        return module

    def shoulder (self, side='', ctrlSize=1):
        name = side + '_shoulder'
        if side == '':
            name = 'shoulder'

        module = self.armModule

        if self.armModule == '':
            module = rig_module(name)

        self.shoulderModule = module

        shoulder = self.clavicleName

        if side != '':
            shoulder = side+ '_' + shoulder

        pm.parent(shoulder, module.skeleton)

        ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
        ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

        self.shoulderControl = rig_control( side=side, name='shoulder', shape='pyramid',
                                    targetOffset=shoulder, modify=1,
                                    parentOffset=module.controls,lockHideAttrs=[
                'tx','ty','tz'], constrain=shoulder, scale =ctrlSize, rotateOrder=0 )

        pm.rotate( pm.PyNode( self.shoulderControl.ctrl+'.cv[:]' ), 0,0,-90, r=True, os=True )

        clavPos = pm.xform(shoulder, translation=True, query=True, ws=True)
        armPos = pm.xform(side+'_'+self.armName, translation=True, query=True, ws=True)
        clavLength = lengthVector( armPos, clavPos )
        if side == 'l':
            pm.move( pm.PyNode( self.shoulderControl.ctrl+'.cv[:]' ), clavLength,0,0, r=True,
                     os=True )
        else:
            pm.move(pm.PyNode(self.shoulderControl.ctrl + '.cv[:]'), -1*clavLength, 0, 0, r=True,
                    os=True)


        if pm.objExists(self.spineConnection):
            pm.parentConstraint(self.spineConnection, self.shoulderControl.offset, mo=True)

        if pm.objExists('rigModules_GRP'):
            pm.parent(module.top, 'rigModules_GRP')

        self.connectArmShoulder(side)
        '''
        quadShoulder
        '''

        name = side+'_quadShoulder'
        if side == '':
            name = 'quadShoulder'

        scapula = self.scapulaName

        if side != '':
            scapula = side+ '_' + scapula

        module = rig_module(name)

        quadShoulderControl = rig_control( side=side, name='quadShoulder', shape='pyramid',
                                        targetOffset=shoulder, modify=1,
                                        parentOffset=module.controls,lockHideAttrs=[
                    'rx','ry','rz'], scale =ctrlSize, rotateOrder=0 )

        self.quadShoulderControl = quadShoulderControl

        clavPos = pm.xform(shoulder, translation=True, query=True, ws=True)
        armPos = pm.xform(scapula, translation=True, query=True, ws=True)
        clavLength = lengthVector( armPos, clavPos )
        if side == 'l':
            pm.move( pm.PyNode( quadShoulderControl.offset ), clavLength,0,0, r=True,
                     os=True )
        else:
            pm.move(pm.PyNode(quadShoulderControl.offset), -1*clavLength, 0, 0, r=True,
                    os=True)
        pm.rotate( pm.PyNode( quadShoulderControl.offset ), 0,0,-90, r=True, os=True )
        

        pm.parentConstraint( 'spineJF_JNT', quadShoulderControl.offset, mo=True )

        clavicleAim = rig_transform(0, name=side + '_clavicleAim', type='locator',
                                        parent=module.parts, target=shoulder).object
        armAim = rig_transform(0, name=side + '_quadShoulderAim', type='locator',
                                parent=module.parts).object


        pm.pointConstraint( 'spineJF_JNT', clavicleAim,mo=True )
        pm.pointConstraint( quadShoulderControl.con, armAim )

        quadShoulderAimTop = mm.eval('rig_makePiston("'+clavicleAim+'", "'+armAim+'", "'+side+'_quadShoulderAim");')


        #pm.orientConstraint( clavicleAim, side+'_shoulder_CTRL', mo=True )
        
        pm.delete(pm.listRelatives(side+'_shoulderOffset_GRP', type='constraint'))
        pm.parentConstraint( clavicleAim, side+'_shoulderOffset_GRP', mo=True )

        pm.addAttr(quadShoulderControl.ctrl, longName='followArm',
                               at='float', k=True, min=0,
                               max=10, defaultValue=3)

        pm.connectAttr( quadShoulderControl.ctrl.followArm, side+'_shoulder_CTRL.followArm'  )

        pm.transformLimits(quadShoulderControl.ctrl, tx=(-1 * self.quadShoulderBaseLimit, self.quadShoulderBaseLimit), etx=(1, 1))
        pm.transformLimits(quadShoulderControl.ctrl, ty=(-1 * self.quadShoulderBaseLimit, self.quadShoulderBaseLimit), ety=(1, 1))
        pm.transformLimits(quadShoulderControl.ctrl, tz=(-1 * self.quadShoulderBaseLimit, self.quadShoulderBaseLimit), etz=(1, 1))

        scapulaControl = rig_control( side=side, name='quadScapula', shape='box',
                                        targetOffset=side+'_scapulaJEnd_JNT', modify=1,
                                        parentOffset=module.controls,lockHideAttrs=[
                    'rx','ry','rz'], scale =ctrlSize, rotateOrder=0 )

        pm.delete( pm.orientConstraint( scapula, scapulaControl.offset ) )


        scapulaAim = rig_transform(0, name=side + '_quadScapulaAim', type='locator',
                                        parent=module.parts).object
        scapulaEndAim = rig_transform(0, name=side + '_quadScapulaEndAim', type='locator',
                                parent=module.parts).object

        pm.delete( pm.parentConstraint(scapula, scapulaAim ) )
        pm.pointConstraint( shoulder, scapulaAim,mo=True )
        pm.pointConstraint( scapulaControl.con, scapulaEndAim )
        pm.delete( pm.orientConstraint( scapula, scapulaEndAim ) )

        quadScapulaAimTop = mm.eval('rig_makePiston("'+scapulaAim+'", "'+scapulaEndAim+'", "'+side+'_quadScapulaAim");')

        #pm.parentConstraint( side+'_clavicleJA_JNT', 'spineJE_JNT', scapulaControl.offset, mo=True )

        constrainObject(  scapulaControl.offset,
                    [shoulder,'spineJE_JNT'], '', [],
                     type='parentConstraint', doSpace=0, setVal=(0.5,1))

        pm.transformLimits(scapulaControl.ctrl, tx=(-1 * self.scapulaBaseLimit, self.scapulaBaseLimit), etx=(1, 1))
        pm.transformLimits(scapulaControl.ctrl, ty=(-1 * self.scapulaBaseLimit, self.scapulaBaseLimit), ety=(1, 1))
        pm.transformLimits(scapulaControl.ctrl, tz=(-1 * self.scapulaBaseLimit, self.scapulaBaseLimit), etz=(1, 1))


        pm.orientConstraint( scapulaAim, scapula, mo=True )

        pm.hide(side+'_shoulderOffset_GRP')

        pm.parent( quadShoulderAimTop, quadScapulaAimTop, module.parts )

        fkCtrls = self.armControls['fk']
        pm.parentConstraint( self.quadShoulderControl.con , fkCtrls[0].offset,
                             mo=True )

        pm.parentConstraint( shoulder, self.armTop,
                             mo=True )

        cmds.dgdirty(allPlugs=True)
        cmds.refresh()

        return module

    def connectArmShoulder(self, side=''):

        if side != '':
            side = side+'_'

        hand = self.armControls['handB']

        handAim = rig_transform(0, name=side + 'handAim', type='locator',
                                    parent=self.armModule.parts).object
        shoulderAim = rig_transform(0, name=side + 'shoulderAim', type='locator',
                                parent=self.armModule.parts).object

        pm.pointConstraint( hand.con, handAim )
        pm.pointConstraint( self.shoulderControl.con, shoulderAim )

        pistonTop = mm.eval('rig_makePiston("'+handAim+'", "'+shoulderAim+'", "'+side+'shoulderAim");')


        pistonChildren = pm.listRelatives( pistonTop, type='transform', c=True)

        pm.parentConstraint(self.spineConnection, pistonTop, mo=True)

        for child in pistonChildren:
            if child.stripNamespace().endswith('shoulderAim_LOCAimOffset'):
                pm.delete(pm.listRelatives(child, type='constraint'))
                pm.parentConstraint(self.spineConnection, child, mo=True )
            if child.stripNamespace().endswith('shoulderAim_LOC'):
                con = pm.parentConstraint( self.shoulderControl.offset, child,
                                           self.shoulderControl.modify,
                                          mo=True)
                pm.setAttr(con.interpType, 0)
                childConAttr = con.getWeightAliasList()[1]
                pm.addAttr(self.shoulderControl.ctrl, longName='followArm',
                           at='float', k=True, min=0,
                           max=10, defaultValue=3)
                pm.setDrivenKeyframe(childConAttr,
                                     cd=self.shoulderControl.ctrl.followArm,
                                     dv=0,
                                     v=0)
                pm.setDrivenKeyframe(childConAttr,
                                     cd=self.shoulderControl.ctrl.followArm,
                                     dv=10,
                                     v=1)
            if child.stripNamespace().endswith('handAim_LOCAimOffset'):
                pm.delete(pm.listRelatives(child, type='constraint'))
                pm.pointConstraint(hand.con, child, mo=True)

        # constrain auto pv
        pm.parentConstraint( side+'handAim_JNT', side+'shoulderAim_JNT',
                             side+'autoArmPVOffset_GRP', mo=True )

        pm.parent(pistonTop, self.armModule.parts)

    def arm (self, side, ctrlSize = 1):
        name = side + '_arm'
        if side == '':
            name = 'arm'

        secColour = 'green'
        if side == 'r':
            secColour = 'magenta'
        elif side == 'l':
            secColour = 'deepskyblue'

        module = rig_module(name)
        self.armModule = module

        arm = self.armName
        elbow = self.elbowName
        hand = self.handName
        handB = self.handBName
        fing = self.fngName

        if side != '':
            arm = side + '_' + arm
            elbow = side + '_' + elbow
            hand = side + '_' + hand
            handB = side + '_' + handB
            fing = side + '_' + fing

        chain = [arm, elbow, hand, handB, fing]

        pm.parent(arm, module.skeleton)

        ctrlSize2 = [ctrlSize / 1.5, ctrlSize / 1.5, ctrlSize / 1.5 ]
        ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
        ctrlSizeQuarter = [ctrlSize / 4.0, ctrlSize / 4.0, ctrlSize / 4.0]
        ctrlSizeEight = [ctrlSize / 8.0, ctrlSize / 8.0, ctrlSize / 8.0]
        ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

        self.armTop = rig_transform(0, name=side + '_armTop',
                                    target=arm, parent=module.parts).object

        armSkeletonParts = rig_transform(0, name=side + '_armSkeletonParts',
                                         parent=self.armTop).object

        # chain result
        armResult = rig_transform(0, name=side + '_armResult', type='joint',
                                  target=arm, parent=armSkeletonParts,
                                  rotateOrder=2).object
        elbowResult = rig_transform(0, name=side + '_elbowResult', type='joint',
                                    target=elbow, rotateOrder=2).object
        handResult = rig_transform(0, name=side + '_handResult', type='joint',
                                   target=hand, rotateOrder=2).object
        handBResult = rig_transform(0, name=side + '_handBResult', type='joint',
                                      target=handB, rotateOrder=2).object
        knuckleResult = rig_transform(0, name=side + '_knuckleResult', type='joint',
                                    target=fing, rotateOrder=2).object

        chainResult = [armResult, elbowResult, handResult, handBResult, knuckleResult]

        chainParent(chainResult)
        chainResult.reverse()

        # chain FK
        armFK = rig_transform(0, name=side + '_armFK', type='joint', target=arm,
                              parent=armSkeletonParts, rotateOrder=2).object
        elbowFK = rig_transform(0, name=side + '_elbowFK', type='joint',
                                target=elbow, rotateOrder=2).object
        handFK = rig_transform(0, name=side + '_handFK', type='joint', target=hand, rotateOrder=2
        ).object
        handBFK = rig_transform(0, name=side + '_handBFK', type='joint', target=handB, rotateOrder=2
        ).object
        knuckleFK = rig_transform(0, name=side + '_knuckleFK', type='joint', target=fing, rotateOrder=2
        ).object

        chainFK = [armFK, elbowFK, handFK, handBFK, knuckleFK]

        chainParent(chainFK)
        chainFK.reverse()

        # chain IK
        armIK = rig_transform(0, name=side + '_armIK', type='joint', target=arm,
                              parent=armSkeletonParts, rotateOrder=2).object
        elbowIK = rig_transform(0, name=side + '_elbowIK', type='joint',
                                target=elbow, rotateOrder=2).object
        handIK = rig_transform(0, name=side + '_handIK', type='joint', target=hand, rotateOrder=2
        ).object
        handBIK = rig_transform(0, name=side + '_handBIK', type='joint', target=handB, rotateOrder=2
        ).object
        knuckleIK = rig_transform(0, name=side + '_knuckleIK', type='joint', target=fing, rotateOrder=2
        ).object

        chainIK = [armIK, elbowIK, handIK, handBIK,knuckleIK]

        chainParent(chainIK)
        chainIK.reverse()

        # create ik
        ik = rig_ik(name, armIK, handIK, 'ikRPsolver')
        pm.parent(ik.handle, module.parts)
        pm.hide(ik.handle)

        poleVector = rig_control(side=side, name='armPV', shape='box',
                                 modify=1, lockHideAttrs=['rx', 'ry', 'rz'],
                                 targetOffset=[arm, hand],
                                 parentOffset=module.controls, scale=ctrlSizeEight)

        if side == 'r':
            pm.rotate(poleVector.ctrl.cv, 90, 0, 0, r=True, os=True)
        else:
            pm.rotate(poleVector.ctrl.cv, -90, 0, 0, r=True, os=True)

        pm.connectAttr(module.top.ikFkSwitch, poleVector.offset + '.visibility')

        self.armControls['poleVector'] = poleVector

        pm.delete(pm.aimConstraint(elbow, poleVector.offset, mo=False))

        handPos = pm.xform(hand, translation=True, query=True, ws=True)
        elbowPos = pm.xform(elbow, translation=True, query=True, ws=True)
        poleVectorPos = pm.xform(poleVector.con, translation=True, query=True,
                                 ws=True)

        pvDistance = lengthVector(elbowPos, poleVectorPos)

        pm.xform(poleVector.offset, translation=[pvDistance, 0, 0], os=True,
                 r=True)

        pm.rotate(poleVector.ctrl.cv, 0, 0, 90, r=True, os=True)

        pm.poleVectorConstraint(poleVector.con, ik.handle)  # create pv

        # pm.move(poleVector.offset, [0, -pvDistance*40, 0], relative=True,
        #       objectSpace=True)

        pvDistance = lengthVector(handPos, elbowPos)
        pm.move(poleVector.offset, [pvDistance * 2, 0, 0], relative=True, objectSpace=True)
        #pm.move(poleVector.offset, [0, 0, pvDistance * 2],relative=True, worldSpace=True)

        print 'ik handle ' + ik.handle

        # ## MAKE FOOT CONTROL
        handControl = rig_control(side=side, name='hand', shape='box', modify=2,
                                  parentOffset=module.controls, lockHideAttrs=['rx', 'ry', 'rz'], scale=ctrlSizeHalf,
                                  rotateOrder=2)

        pm.delete(pm.pointConstraint(hand, handControl.offset))

        handControl.gimbal = createCtrlGimbal(handControl)
        handControl.pivot = createCtrlPivot(handControl)

        '''
        constrainObject(handControl.offset,
                        [self.pelvisConnection, self.centerConnection,self.spineFullBodyCtrl.con,
                         'worldSpace_GRP'],
                        handControl.ctrl, ['pelvis', 'spineLower', 'fullBody' , 'world'],
                        type='parentConstraint')
        '''


        pm.connectAttr(module.top.ikFkSwitch, handControl.offset + '.visibility')

        self.armControls['hand'] = handControl

        # auto pole vector LOCATOR
        autoPVOffset = rig_transform(0, name=side + '_autoArmPVOffset',
                                     parent=module.parts, target=poleVector.con
        ).object
        autoPVLoc = rig_transform(0, name=side + '_autoArmPV', type='locator',
                                  parent=autoPVOffset, target=autoPVOffset).object

        #pm.parentConstraint(self.centerConnection, autoPVOffset, mo=True)
        #pm.pointConstraint(self.centerConnection, handControl.con, autoPVLoc, mo=True)

        constrainObject(poleVector.offset,
                        [autoPVLoc, self.pelvisConnection, self.centerConnection,
                         'worldSpace_GRP'],
                        poleVector.ctrl, ['auto', 'pelvis', 'spineLower', 'world'],
                        type='parentConstraint')

        rig_curveBetweenTwoPoints(poleVector.con, elbow, name=name+'PV')

        # ## MAKE FOOT BALL CONTROL
        handBallControl = rig_control(side=side, name='handBall', shape='box', modify=2,
                                      parentOffset=module.controls, scale=ctrlSize2,
                                      rotateOrder=2, colour=secColour)

        handBallControl.gimbal = createCtrlGimbal(handBallControl)
        handBallControl.pivot = createCtrlPivot(handBallControl)

        self.armControls['handB'] = handBallControl

        pm.delete(pm.pointConstraint(handB, handBallControl.offset))
        #pm.parentConstraint(handBallControl.con, ik.handle, mo=True)

        constrainObject(handBallControl.offset,
                        [self.pelvisConnection, self.centerConnection,self.spineFullBodyCtrl.con,
                         'worldSpace_GRP'],
                        handBallControl.ctrl, ['pelvis', 'spineLower', 'fullBody' , 'world'],
                        type='parentConstraint', setSpace=3)
        

        pm.connectAttr(module.top.ikFkSwitch, handBallControl.offset + '.visibility')

        pm.rotate(handBallControl.ctrl.cv, [90, 0, 0], relative=True, objectSpace=True)
        pm.move(handBallControl.ctrl.cv, [0, 0.5, 0], relative=True)

        pm.addAttr(handBallControl.ctrl, ln='MOTION', at='enum',
                   enumName='___________',
                   k=True)
        handBallControl.ctrl.MOTION.setLocked(True)
        pm.addAttr(handBallControl.ctrl, longName='twist', at='float', k=True)
        pm.addAttr(handBallControl.ctrl, longName='handRoll', at='float', k=True, min=0,
                   max=10, dv=0)
        pm.connectAttr(handBallControl.ctrl.twist, ik.handle.twist)

        '''
        constrainObject(handBallControl.modify[0],
                        [handBallControl.offset, 'worldSpace_GRP'],
                        handBallControl.ctrl, ['hand', 'world'],
                        type='orientConstraint')
        '''


        ### MAKE FOOT TOES CONTROL
        handToesControl = rig_control(side=side, name='handToes', shape='cylinder', modify=2,
                                      parentOffset=module.controls, scale=ctrlSizeQuarter,
                                      rotateOrder=2, colour=secColour)

        pm.delete(pm.pointConstraint(fing, handToesControl.offset))
        pm.parent( handToesControl.offset, handBallControl.con )
        pm.parent(  ik.handle, handToesControl.con )

        pm.connectAttr(module.top.ikFkSwitch, handToesControl.offset + '.visibility')

        pm.rotate(handToesControl.ctrl.cv, [0, 0, 90], relative=True, objectSpace=True)

        
        constrainObject(handToesControl.modify[0],
                        [handToesControl.offset, 'worldSpace_GRP'],
                        handToesControl.ctrl, ['hand', 'world'],
                        type='orientConstraint')
        

        pm.parentConstraint( handToesControl.con, handControl.offset , mo=True)

        pm.parent( handControl.offset, handBallControl.con )
        
        ## MAKE FOOT ROLLS
        pm.addAttr(handBallControl.ctrl, ln='ROLLS', at='enum',
                   enumName='___________',
                   k=True)
        handBallControl.ctrl.ROLLS.setLocked(True)
        rollTip = rig_transform(0, name=side + '_handRollTip',
                                    parent=handBallControl.gimbal.ctrl,
                                    target=side+'_handRollTip_LOC').object
        rollHeel = rig_transform(0, name=side + '_handRollHeel',
                            parent=rollTip,
                            target=side + '_handRollHeel_LOC').object
        rollIn = rig_transform(0, name=side + '_handRollIn',
                             parent=rollHeel,
                             target=side + '_handRollIn_LOC').object
        rollOut = rig_transform(0, name=side + '_handRollOut',
                               parent=rollIn,
                               target=side + '_handRollOut_LOC').object
        pm.parent( handBallControl.con, rollOut )

        pm.delete(pm.ls(side+"_handRoll*_LOC"))

        pm.addAttr(handBallControl.ctrl, longName='rollTip', at='float', k=True, min=0,
                   max=10, dv=0)
        pm.addAttr(handBallControl.ctrl, longName='rollHeel', at='float', k=True, min=0,
                   max=10, dv=0)
        pm.addAttr(handBallControl.ctrl, longName='rollIn', at='float', k=True, min=0,
                   max=10, dv=0)
        pm.addAttr(handBallControl.ctrl, longName='rollOut', at='float', k=True, min=0,
                   max=10, dv=0)

        flipRoll = 1
        if side == 'r':
            flipRoll = -1
        rig_animDrivenKey(handBallControl.ctrl.rollTip, (0, 10),
                          rollTip+'.rotateX', (0, 90 ))
        rig_animDrivenKey(handBallControl.ctrl.rollHeel, (0, 10),
                          rollHeel+'.rotateX', (0, -90 ))
        rig_animDrivenKey(handBallControl.ctrl.rollIn, (0, 10),
                          rollIn+'.rotateZ', (0, 90*flipRoll ))
        rig_animDrivenKey(handBallControl.ctrl.rollOut, (0, 10),
                          rollOut + '.rotateZ', (0, -90*flipRoll ))

        ## do hand roll with handBall and handToes modify
        rig_animDrivenKey(handBallControl.ctrl.handRoll, (0,5, 10),
                          handToesControl.modify[1] + '.rotateX', (0, 20,30 ))
        #rig_animDrivenKey(handBallControl.ctrl.handRoll, (0, 5, 10),
        #                  handToesControl.modify[1] + '.rotateX', (0, 0, 40 ))
        
        

        # ## MAKE TOES CONTROL
        knuckleControl = rig_control(side=side, name='fing', shape='pyramid', modify=1,
                                     parentOffset=module.controls, scale=ctrlSizeQuarter,
                                     rotateOrder=2, lockHideAttrs=['tx','ty','tz'])

        self.armControls['fing'] = knuckleControl

        pm.delete(pm.parentConstraint(fing, knuckleControl.offset))
        pm.orientConstraint(knuckleControl.con, knuckleIK, mo=True)
        pm.parentConstraint(handToesControl.con, knuckleControl.offset, mo=True)

        pm.connectAttr(module.top.ikFkSwitch, knuckleControl.offset + '.visibility')

        
        constrainObject(knuckleControl.modify,
                        [handBallControl.con, knuckleControl.offset, 'worldSpace_GRP'],
                        knuckleControl.ctrl, ['handBall', 'handToes', 'world'],
                        type='orientConstraint')
        

        knucklePos = pm.xform(knuckleControl.con, translation=True, query=True, ws=True)
        endPos = pm.xform(side + '_knuckleJEnd_JNT', translation=True, query=True, ws=True)

        knuckleLength = lengthVector(knucklePos, endPos)

        pm.move(knuckleControl.ctrl.cv, [0, 0, knuckleLength], relative=True)

        pm.addAttr(knuckleControl.ctrl, ln='SHAPE', at='enum',
                   enumName='___________',
                   k=True)
        knuckleControl.ctrl.SHAPE.setLocked(True)
        pm.addAttr(knuckleControl.ctrl, longName='curl', at='float', k=True, min=-10,
                   max=10, dv=0)
        pm.addAttr(knuckleControl.ctrl, longName='curlThumb', at='float', k=True, min=-10,
                   max=10, dv=0)
        pm.addAttr(knuckleControl.ctrl, longName='splay', at='float', k=True, min=-10,
                   max=10, dv=0)


        '''
        if side == 'l':
            pm.move(toesControl.ctrl.cv, [0, 0, toesLength], relative=True)
        else:
            pm.move(toesControl.ctrl.cv, [0, 0, toesLength * -1], relative=True)
        '''

        # make reverse wrist ik setup
        pm.parent( handBIK, armSkeletonParts  )
        handBReverseJnt = rig_transform(0, name=side + '_handBReverse', type='joint',
                                parent=armSkeletonParts, target=handBIK).object
        wristReverseJnt = rig_transform(0, name=side + '_wristReverse', type='joint',
                                parent=armSkeletonParts, target = handIK).object
        pm.parent( wristReverseJnt, handBReverseJnt )
        wristIK = rig_ik( side+'_wrist' ,handBReverseJnt, wristReverseJnt, 'ikRPsolver' )
        #pm.parent(wristIK.handle, module.parts)
        pm.hide(wristIK.handle)
        pm.parent(wristIK.handle, handToesControl.con)
        wristPV = rig_transform(0, name=side + '_wristPV', type='locator',
                                parent=module.parts, target=handBallControl.con).object
        pm.move(wristPV, [50, 0, 0],relative=True, objectSpace=True)
        pm.parentConstraint( handToesControl.con, wristPV, mo=True )
        pm.poleVectorConstraint(wristPV, wristIK.handle)
        pm.pointConstraint( handControl.con, wristIK.handle, mo=True )
        pm.parentConstraint( handToesControl.con,handBReverseJnt,mo=True )

        pm.pointConstraint(wristReverseJnt, ik.handle, mo=True)
        pm.orientConstraint( wristReverseJnt, handIK, mo=True )

        # make arm aim
        armAimLoc = rig_transform(0, name=side + '_armFootAim', type='locator',
                                    parent=module.parts).object
        handAimLoc = rig_transform(0, name=side + '_handArmAim', type='locator',
                                parent=module.parts).object

        pm.pointConstraint( self.armTop, armAimLoc  )
        pm.delete(pm.pointConstraint( handBallControl.con, handAimLoc ))
        pm.pointConstraint( handToesControl.con, handAimLoc,mo=True  )
        pm.setAttr( handAimLoc+'.rotateZ', -90 )
        pm.setAttr(armAimLoc+'.rotateZ', -90)

        armAimTop = mm.eval('rig_makePiston("'+armAimLoc+'", "'+handAimLoc+'", "'+side+'_armAim");')

        #armAimMod = rig_transform(0, name=side + '_armFootAimModify', type='group',
         #                           parent=side+'_handArmAim_LOC', target=side+'_handArmAim_LOC').object

        #pm.parent( side+'_handArmAim_JNT', armAimMod )

        pm.parent( armAimTop, module.parts )

        # make hand wrist aim
        wristAimLoc = rig_transform(0, name=side + '_wristArmAim', type='locator',
                                parent=module.parts).object
        handBAimLoc = rig_transform(0, name=side + '_handBAim', type='locator',
                                    parent=module.parts).object

        pm.parentConstraint( handIK, wristAimLoc  )
        pm.delete(pm.orientConstraint( handIK, handBAimLoc ))
        pm.pointConstraint( handBReverseJnt, handBAimLoc )
        #pm.setAttr( handAimLoc+'.rotateZ', -90 )
        #pm.setAttr(armAimLoc+'.rotateZ', -90)

        wristAimTop = mm.eval('rig_makePiston("'+wristAimLoc+'", "'+handBAimLoc+'", "'+side+'_wristAim");')

        pm.parent( wristAimTop, module.parts )
        pm.parentConstraint( side+'_wristArmAim_JNT', handBIK, skipRotate=('x','y','z'), mo=True )
        pm.parentConstraint( handToesControl.con, handBIK, skipTranslate=('x','y','z'), mo=True )

        # make wrist bend
        startMeasure = rig_transform(0, name=name+'FullStart', type='locator',
                                  parent=module.parts, target=arm).object
        endMeasure = rig_transform(0, name=name+'FullEnd', type='locator',
                                  parent=module.parts, target=handToesControl.con).object
        totalArmDist = rig_measure(name=name+'FullLength', start=startMeasure, end=endMeasure,
                            parent=module.parts)

        armDistGlobal_MD = multiDivideNode( name+'_distanceRotationGlobal', 'multiply',
                        'rig_GRP', 'worldScale', '', totalArmDist.distanceVal )
        armDist_MD = multiDivideNode( name+'_distanceRotation', 'divide',
                        totalArmDist.distance, 'distance', armDistGlobal_MD, 'outputX' )

        pm.pointConstraint( handBallControl.con, endMeasure, mo=True )
        pm.pointConstraint( self.pelvisConnection, startMeasure, mo=True )

        '''

        expression -e -s "float $outputX = multiplyDivide8.outputX; \n\nfloat $degrees = 0;\n\n$degrees = -1*atand(1.0-$outputX);\n\nl_handAim_JNT.rotateZ = $degrees*1.5;"  -o "" -ae 1 -uc all  l_armRotate_EXP;

        
        '''
        mm.eval('expression -o ("'+side+'_handArmAim_JNT") -s ("float $outputX = '+armDist_MD+'.outputX; float $degrees = 0;$degrees = -1*atand(1.0-$outputX);ry = $degrees*1.5;") -n ("'+side+'_armRotate_EXP") -ae 1 -uc all ;')

        handOrientLoc = rig_transform(0, name=side+'_handOrient', type='locator',
                                  parent=side+'_handArmAim_JNT', target=handControl.con).object
        pm.setAttr( handOrientLoc+'.tx', 0)
        pm.setAttr( handOrientLoc+'.ty', 0)
        pm.setAttr( handOrientLoc+'.tz', 0)
        con = pm.parentConstraint( handControl.offset, handOrientLoc, handControl.modify[0], mo=True )
        pm.parentConstraint( side+'_armFootAim_JNT', side+'_handArmAim_JNT', autoPVOffset, mo=True )

        
        # create ik stretchy and soft pop
        endBlendLoc = rig_ikStretchySoftPop(side, name, chainIK, module, handControl,
                                            ctrlSizeQuarter,
                                            self.armTop)

        #pm.pointConstraint(endBlendLoc, handToesControl.offset, mo=True)

        pm.addAttr(handBallControl.ctrl, ln='ikSettings', at='enum',
                 enumName='___________',
                 k=True)
        handBallControl.ctrl.ikSettings.setLocked(True)

        pm.addAttr( handBallControl.ctrl, longName='ikStretch', shortName='iks',attributeType="double",
                                min=0, max=1, defaultValue=0, keyable=True )
        pm.addAttr( handBallControl.ctrl, longName='midSlide', shortName='es',attributeType="double",
                                    min=-1, max=1, defaultValue=0, keyable=True )
        pm.addAttr( handBallControl.ctrl, longName='wristStiffness', shortName='aksti',attributeType="double",
                                    min=0, max=1, defaultValue=0.5, keyable=True )

        targets = con.getWeightAliasList()
        pm.connectAttr( handBallControl.ctrl.wristStiffness, targets[0] )
        connectReverse( name=side+'_wristOrient_reverseNode#', input=(targets[0],0,0), output=(targets[1],0,0) )

        pm.connectAttr( handBallControl.ctrl.ikStretch, handControl.ctrl.ikStretch)
        pm.connectAttr( handBallControl.ctrl.midSlide, handControl.ctrl.midSlide)
        pm.setAttr( handControl.ctrl.ikSettings, k=False, cb=False )
        pm.setAttr( handControl.ctrl.ikStretch, k=False, cb=False )
        pm.setAttr( handControl.ctrl.ikSoftBlend, k=False, cb=False )
        pm.setAttr( handControl.ctrl.midSlide, k=False, cb=False )

        # create fk
        print 'fk chain ' + str(chainFK)
        fkCtrls = fkControlChain(chainFK, scale=ctrlSize)
        for fk in fkCtrls:
            pm.parent(fk.offset, module.controls)
            pm.setDrivenKeyframe(fk.offset + '.visibility',
                                 cd=module.top.ikFkSwitch,
                                 dv=1,
                                 v=0)
            pm.setDrivenKeyframe(fk.offset + '.visibility',
                                 cd=module.top.ikFkSwitch,
                                 dv=0,
                                 v=1)
        
        '''
        elbowFk = fkCtrls[1]
        rotateAxis = ['rx', 'ry', 'rz']
        if self.elbowAxis in rotateAxis: rotateAxis.remove(self.elbowAxis)
        for at in rotateAxis:
            elbowFk.ctrl.attr(at).setKeyable(False)
            elbowFk.ctrl.attr(at).setLocked(True)
        '''
        self.armControls['fk'] = fkCtrls

        self.connectIkFkSwitch(chains=[chainResult, chainIK, chainFK],
                               module=module, name=name)

        # constrain result to skeleton
        for i in range(0, len(chain)):
            pm.parentConstraint(chainResult[i], chain[i], mo=True)

        cmds.dgdirty(allPlugs=True)
        cmds.refresh()

        return module

    def hand(self, side='', axis='rz',ctrlSize=1.0, baseLimit=0.2):
        abc = list(string.ascii_lowercase)

        name = side + '_fingers'
        sideName = side + '_'
        if side == '':
            name = 'fingers'
            sideName = ''



        module = rig_module(name)
        self.fingersModule = module

        ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
        ctrlSize = [ctrlSize, ctrlSize, ctrlSize]



        rotateAxis = ['rx','ry','rz']

        rotateAxis.remove(axis)

        #skipAxis = rotateAxis + ['tx', 'ty','tz' ]
        skipAxis =  ['tx', 'ty','tz' ]

        for finger in ( self.fngThumb, self.fngIndex, self.fngMid, self.fngRing,
                        self.fngPinky ):

            fng = finger

            if side != '':
                fng = side + '_' + fng

            #print 'finger is '+fng
            if pm.objExists(fng):

                chainFingers = rig_chain( fng )

                childrenFngs = chainFingers.chainChildren

                childrenFngs.pop(len(childrenFngs)-1)

                sc = simpleControls(fng,
                               modify=2, scale=ctrlSize,
                               parentOffset=module.controls)

                fngCtrl = sc[fng]
                #baseLimit = 0.2
                pm.transformLimits( fngCtrl.ctrl, tx=(-1*baseLimit, baseLimit), etx=(1, 1))
                pm.transformLimits( fngCtrl.ctrl, ty=(-1*baseLimit, baseLimit), ety=(1, 1))
                pm.transformLimits( fngCtrl.ctrl, tz=(-1*baseLimit, baseLimit), etz=(1, 1))

                if 'Thumb' in fng:
                    if pm.objExists(sideName+'handJA_JNT'):
                        pm.parentConstraint(  sideName+'handJA_JNT', fngCtrl.offset, mo=True)
                else:
                    if pm.objExists(sideName + 'handJB_JNT'):
                        pm.parentConstraint(sideName + 'handJA_JNT', fngCtrl.offset, mo=True)
                        pm.orientConstraint(sideName + 'handJB_JNT', fngCtrl.modify[0], mo=True, skip='x')

                sc = simpleControls(childrenFngs,
                               modify=2, scale=ctrlSize,
                               parentOffset=module.controls,
                               lockHideAttrs=skipAxis)

                # fk control
                armControl = self.armControls['fing'].ctrl
                if 'Thumb' in fng:
                    if pm.objExists(armControl.curlThumb):
                        for key in sc:
                            control = sc[key]
                            rig_animDrivenKey(armControl.curlThumb, (-10, 0, 10),
                                              control.modify[0] + '.rotateZ', (-90, 0, 90 ))

                        rig_animDrivenKey(armControl.curlThumb, (-10, 0, 10),
                                          fngCtrl.modify[1] + '.rotateZ', (-90, 0, 90 ))
                else:
                    if pm.objExists(armControl.curl):
                        for key in sc:
                            control = sc[key]
                            rig_animDrivenKey(armControl.curl, (-10, 0, 10),
                                              control.modify[0] + '.rotateZ', (-90, 0, 90 ))

                        rig_animDrivenKey(armControl.curl, (-10, 0, 10),
                                          fngCtrl.modify[1] + '.rotateZ', (-90, 0, 90 ))

                pm.parent( fng, module.skeleton )

            else:
                print fng + ' does not exist...Skipping.'

        cmds.dgdirty(allPlugs=True)
        cmds.refresh()

        return module 

    def pelvis (self, ctrlSize=1):
        name = 'pelvis'

        module = self.spineModule

        if self.spineModule == '':
            module = rig_module(name)

        self.pelvisModule = module

        pelvis = self.pelvisConnection

        pm.parent(pelvis, module.skeleton)

        print 'pelvis ' + pelvis

        ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
        ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

        self.pelvisControl = rig_control(side='', name='pelvis', shape='box',
                                           targetOffset=pelvis, modify=1, colour='green',
                                           parentOffset=module.controls, lockHideAttrs=[
                'tx', 'ty', 'tz'], constrain=pelvis, scale=ctrlSize, rotateOrder=0)

        if pm.objExists(self.centerConnection):
            pm.parentConstraint(self.centerConnection, self.pelvisControl.offset, mo=True)

        if pm.objExists('rigModules_GRP'):
            pm.parent(module.top, 'rigModules_GRP')

        pm.scale(pm.PyNode(self.pelvisControl.ctrl + '.cv[:]'), 1, 0.3, 1)

        cmds.dgdirty(allPlugs=True)
        cmds.refresh()

        return module

    def connectLegPelvis(self):

            fkCtrls = self.legControls['fk']
            #foot = self.legControls['foot']

            print 'self.pelvisControl ' + str(self.pelvisControl.ctrl)
            pm.parentConstraint(self.pelvisControl.con, fkCtrls[0].offset,
                                mo=True)
            pm.parentConstraint(self.pelvisControl.con, self.legTop,
                                mo=True)

            '''
            hipControl = rig_control(side=side, name='hip', shape='sphere', modify=1,
                                     parentOffset=module.controls, scale=ctrlSizeHalf,
                                     rotateOrder=2, lockHideAttrs=['rx', 'ry', 'rz'])

            constrainObject(hipControl.offset,
                            [self.pelvisConnection, self.centerConnection,
                             'worldSpace_GRP'],
                            poleVector.ctrl, ['pelvis', 'main', 'world'],
                            type='parentConstraint')
            '''

    def leg (self, side='', ctrlSize=1.0, **kwds):

        self.prefix = defaultReturn('', 'prefix', param=kwds)
        self.doRolls = defaultReturn(1, 'doRolls', param=kwds)

        prefix = self.prefix

        name = side + '_leg'+prefix
        if side == '':
            name = 'leg'+prefix

        secColour = 'green'
        if side == 'r':
            secColour = 'magenta'
        elif side == 'l':
            secColour = 'deepskyblue'

        module = rig_module(name)
        self.legModule = module

        leg = self.legName
        knee = self.kneeName
        foot = self.footName
        footB = self.footBName
        toes = self.toesName

        if side != '':
            leg = side + '_' + leg
            knee = side + '_' + knee
            foot = side + '_' + foot
            footB = side + '_' + footB
            toes = side + '_' + toes

        chain = [leg, knee, foot, footB, toes]

        pm.parent(leg, module.skeleton)

        ctrlSize2 = [ctrlSize / 1.5, ctrlSize / 1.5, ctrlSize / 1.5 ]
        ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
        ctrlSizeQuarter = [ctrlSize / 4.0, ctrlSize / 4.0, ctrlSize / 4.0]
        ctrlSizeEight = [ctrlSize / 8.0, ctrlSize / 8.0, ctrlSize / 8.0]
        ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

        self.legTop = rig_transform(0, name=name+'Top',
                                    target=leg, parent=module.parts).object

        legSkeletonParts = rig_transform(0, name=name+'SkeletonParts',
                                         parent=self.legTop).object

        # chain result
        legResult = rig_transform(0, name=name+'Result', type='joint',
                                  target=leg, parent=legSkeletonParts,
                                  rotateOrder=2).object
        kneeResult = rig_transform(0, name=side + '_knee'+prefix+'Result', type='joint',
                                    target=knee, rotateOrder=2).object
        footResult = rig_transform(0, name=side + '_foot'+prefix+'Result', type='joint',
                                   target=foot, rotateOrder=2).object
        footBResult = rig_transform(0, name=side + '_footB'+prefix+'Result', type='joint',
                                      target=footB, rotateOrder=2).object
        toesResult = rig_transform(0, name=side + '_toes'+prefix+'Result', type='joint',
                                    target=toes, rotateOrder=2).object

        chainResult = [legResult, kneeResult, footResult, footBResult, toesResult]

        chainParent(chainResult)
        chainResult.reverse()

        # chain FK
        legFK = rig_transform(0, name=name+'FK', type='joint', target=leg,
                              parent=legSkeletonParts, rotateOrder=2).object
        kneeFK = rig_transform(0, name=side + '_knee'+prefix+'FK', type='joint',
                                target=knee, rotateOrder=2).object
        footFK = rig_transform(0, name=side + '_foot'+prefix+'FK', type='joint', target=foot, rotateOrder=2
        ).object
        footBFK = rig_transform(0, name=side + '_footB'+prefix+'FK', type='joint', target=footB, rotateOrder=2
        ).object
        toesFK = rig_transform(0, name=side + '_toes'+prefix+'FK', type='joint', target=toes, rotateOrder=2
        ).object

        chainFK = [legFK, kneeFK, footFK, footBFK, toesFK]

        chainParent(chainFK)
        chainFK.reverse()

        # chain IK
        legIK = rig_transform(0, name=name+'IK', type='joint', target=leg,
                              parent=legSkeletonParts, rotateOrder=2).object
        kneeIK = rig_transform(0, name=side + '_knee'+prefix+'IK', type='joint',
                                target=knee, rotateOrder=2).object
        footIK = rig_transform(0, name=side + '_foot'+prefix+'IK', type='joint', target=foot, rotateOrder=2
        ).object
        footBIK = rig_transform(0, name=side + '_footB'+prefix+'IK', type='joint', target=footB, rotateOrder=2
        ).object
        toesIK = rig_transform(0, name=side + '_toes'+prefix+'IK', type='joint', target=toes, rotateOrder=2
        ).object

        chainIK = [legIK, kneeIK, footIK, footBIK,toesIK]

        chainParent(chainIK)
        chainIK.reverse()

        # create ik
        ik = rig_ik(name, legIK, footIK, 'ikRPsolver')
        pm.parent(ik.handle, module.parts)
        pm.hide(ik.handle)

        poleVector = rig_control(side=side, name='leg'+prefix+'PV', shape='box',
                                 modify=1, lockHideAttrs=['rx', 'ry', 'rz'],
                                 targetOffset=[leg, foot],
                                 parentOffset=module.controls, scale=ctrlSizeEight)

        if side == 'r':
            pm.rotate(poleVector.ctrl.cv, 90, 0, 0, r=True, os=True)
        else:
            pm.rotate(poleVector.ctrl.cv, -90, 0, 0, r=True, os=True)

        pm.connectAttr(module.top.ikFkSwitch, poleVector.offset + '.visibility')

        self.legControls['poleVector'] = poleVector

        pm.delete(pm.aimConstraint(knee, poleVector.offset, mo=False))

        footPos = pm.xform(foot, translation=True, query=True, ws=True)
        kneePos = pm.xform(knee, translation=True, query=True, ws=True)
        poleVectorPos = pm.xform(poleVector.con, translation=True, query=True,
                                 ws=True)

        pvDistance = lengthVector(kneePos, poleVectorPos)

        pm.xform(poleVector.offset, translation=[pvDistance, 0, 0], os=True,
                 r=True)

        pm.rotate(poleVector.ctrl.cv, 0, 0, 90, r=True, os=True)

        pm.poleVectorConstraint(poleVector.con, ik.handle)  # create pv

        # pm.move(poleVector.offset, [0, -pvDistance*40, 0], relative=True,
        #       objectSpace=True)

        pvDistance = lengthVector(footPos, kneePos)
        pm.move(poleVector.offset, [pvDistance * 2, 0, 0], relative=True, objectSpace=True)
        #pm.move(poleVector.offset, [0, 0, pvDistance * 2],relative=True, worldSpace=True)

        print 'ik handle ' + ik.handle

        # ## MAKE FOOT CONTROL
        footControl = rig_control(side=side, name='foot'+prefix, shape='box', modify=2,
                                  parentOffset=module.controls, lockHideAttrs=['rx', 'ry', 'rz'], scale=ctrlSizeHalf,
                                  rotateOrder=2)

        pm.delete(pm.pointConstraint(foot, footControl.offset))

        footControl.gimbal = createCtrlGimbal(footControl)
        footControl.pivot = createCtrlPivot(footControl)

        '''
        constrainObject(footControl.offset,
                        [self.pelvisConnection, self.centerConnection,self.spineFullBodyCtrl.con,
                         'worldSpace_GRP'],
                        footControl.ctrl, ['pelvis', 'spineLower', 'fullBody' , 'world'],
                        type='parentConstraint')
        '''


        pm.connectAttr(module.top.ikFkSwitch, footControl.offset + '.visibility')

        self.legControls['foot'] = footControl

        # auto pole vector LOCATOR
        autoPVOffset = rig_transform(0, name=side + '_autoLeg'+prefix+'PVOffset',
                                     parent=module.parts, target=poleVector.con
        ).object
        autoPVLoc = rig_transform(0, name=side + '_autoLeg'+prefix+'PV', type='locator',
                                  parent=autoPVOffset, target=autoPVOffset).object

        #pm.parentConstraint(self.centerConnection, autoPVOffset, mo=True)
        #pm.pointConstraint(self.centerConnection, footControl.con, autoPVLoc, mo=True)

        constrainObject(poleVector.offset,
                        [autoPVLoc, self.pelvisConnection, self.centerConnection,
                         'worldSpace_GRP'],
                        poleVector.ctrl, ['auto', 'pelvis', 'spineLower', 'world'],
                        type='parentConstraint')

        rig_curveBetweenTwoPoints(poleVector.con, knee, name=name+'PV')

        # ## MAKE FOOT BALL CONTROL
        footBallControl = rig_control(side=side, name='footBall'+prefix, shape='box', modify=2,
                                      parentOffset=module.controls, scale=ctrlSize2,
                                      rotateOrder=2, colour=secColour)

        footBallControl.gimbal = createCtrlGimbal(footBallControl)
        footBallControl.pivot = createCtrlPivot(footBallControl)

        pm.delete(pm.pointConstraint(footB, footBallControl.offset))
        #pm.parentConstraint(footBallControl.con, ik.handle, mo=True)

        constrainObject(footBallControl.offset,
                        [self.pelvisConnection, self.centerConnection,self.spineFullBodyCtrl.con,
                         'worldSpace_GRP'],
                        footBallControl.ctrl, ['pelvis', 'spineLower', 'fullBody' , 'world'],
                        type='parentConstraint', setSpace=3)
        

        pm.connectAttr(module.top.ikFkSwitch, footBallControl.offset + '.visibility')

        pm.rotate(footBallControl.ctrl.cv, [90, 0, 0], relative=True, objectSpace=True)
        pm.move(footBallControl.ctrl.cv, [0, 0.5, 0], relative=True)

        pm.addAttr(footBallControl.ctrl, ln='MOTION', at='enum',
                   enumName='___________',
                   k=True)
        footBallControl.ctrl.MOTION.setLocked(True)
        pm.addAttr(footBallControl.ctrl, longName='twist', at='float', k=True)
        pm.addAttr(footBallControl.ctrl, longName='footRoll', at='float', k=True, min=0,
                   max=10, dv=0)
        pm.connectAttr(footBallControl.ctrl.twist, ik.handle.twist)

        '''
        constrainObject(footBallControl.modify[0],
                        [footBallControl.offset, 'worldSpace_GRP'],
                        footBallControl.ctrl, ['foot', 'world'],
                        type='orientConstraint')
        '''


        ### MAKE FOOT TOES CONTROL
        footToesControl = rig_control(side=side, name='footToes'+prefix, shape='cylinder', modify=2,
                                      parentOffset=module.controls, scale=ctrlSizeQuarter,
                                      rotateOrder=2, colour=secColour)

        pm.delete(pm.pointConstraint(toes, footToesControl.offset))
        pm.parent( footToesControl.offset, footBallControl.con )
        pm.parent(  ik.handle, footToesControl.con )

        pm.connectAttr(module.top.ikFkSwitch, footToesControl.offset + '.visibility')

        pm.rotate(footToesControl.ctrl.cv, [0, 0, 90], relative=True, objectSpace=True)

        
        constrainObject(footToesControl.modify[0],
                        [footToesControl.offset, 'worldSpace_GRP'],
                        footToesControl.ctrl, ['foot', 'world'],
                        type='orientConstraint')
        

        pm.parentConstraint( footToesControl.con, footControl.offset , mo=True)

        pm.parent( footControl.offset, footBallControl.con )
        
        ## MAKE FOOT ROLLS
        if self.doRolls:
            pm.addAttr(footBallControl.ctrl, ln='ROLLS', at='enum',
                       enumName='___________',
                       k=True)
            footBallControl.ctrl.ROLLS.setLocked(True)
            rollTip = rig_transform(0, name=side + '_footRollTip'+prefix,
                                        parent=footBallControl.gimbal.ctrl,
                                        target=side+'_footRollTip'+prefix+'_LOC').object
            rollHeel = rig_transform(0, name=side + '_footRollHeel'+prefix,
                                parent=rollTip,
                                target=side + '_footRollHeel'+prefix+'_LOC').object
            rollIn = rig_transform(0, name=side + '_footRollIn'+prefix,
                                 parent=rollHeel,
                                 target=side + '_footRollIn'+prefix+'_LOC').object
            rollOut = rig_transform(0, name=side + '_footRollOut'+prefix,
                                   parent=rollIn,
                                   target=side + '_footRollOut'+prefix+'_LOC').object
            pm.parent( footBallControl.con, rollOut )

            pm.delete(pm.ls(side+"_footRoll*_LOC"))

            pm.addAttr(footBallControl.ctrl, longName='rollTip', at='float', k=True, min=0,
                       max=10, dv=0)
            pm.addAttr(footBallControl.ctrl, longName='rollHeel', at='float', k=True, min=0,
                       max=10, dv=0)
            pm.addAttr(footBallControl.ctrl, longName='rollIn', at='float', k=True, min=0,
                       max=10, dv=0)
            pm.addAttr(footBallControl.ctrl, longName='rollOut', at='float', k=True, min=0,
                       max=10, dv=0)

            flipRoll = 1
            if side == 'r':
                flipRoll = -1
            rig_animDrivenKey(footBallControl.ctrl.rollTip, (0, 10),
                              rollTip+'.rotateX', (0, 90 ))
            rig_animDrivenKey(footBallControl.ctrl.rollHeel, (0, 10),
                              rollHeel+'.rotateX', (0, -90 ))
            rig_animDrivenKey(footBallControl.ctrl.rollIn, (0, 10),
                              rollIn+'.rotateZ', (0, 90*flipRoll ))
            rig_animDrivenKey(footBallControl.ctrl.rollOut, (0, 10),
                              rollOut + '.rotateZ', (0, -90*flipRoll ))

            ## do foot roll with footBall and footToes modify
            rig_animDrivenKey(footBallControl.ctrl.footRoll, (0,5, 10),
                              footToesControl.modify[1] + '.rotateX', (0, 20,30 ))
            #rig_animDrivenKey(footBallControl.ctrl.footRoll, (0, 5, 10),
            #                  footToesControl.modify[1] + '.rotateX', (0, 0, 40 ))
        
        

        # ## MAKE TOES CONTROL
        toesControl = rig_control(side=side, name='toes'+prefix, shape='pyramid', modify=1,
                                     parentOffset=module.controls, scale=ctrlSizeQuarter,
                                     rotateOrder=2, lockHideAttrs=['tx','ty','tz'])

        self.legControls['toes'] = toesControl

        pm.delete(pm.parentConstraint(toes, toesControl.offset))
        pm.orientConstraint(toesControl.con, toesIK, mo=True)
        pm.parentConstraint(footToesControl.con, toesControl.offset, mo=True)

        pm.connectAttr(module.top.ikFkSwitch, toesControl.offset + '.visibility')

        
        constrainObject(toesControl.modify,
                        [footBallControl.con, toesControl.offset, 'worldSpace_GRP'],
                        toesControl.ctrl, ['footBall', 'footToes', 'world'],
                        type='orientConstraint')
        

        toesPos = pm.xform(toesControl.con, translation=True, query=True, ws=True)
        endPos = pm.xform(side + '_toes'+prefix+'JEnd_JNT', translation=True, query=True, ws=True)

        toesLength = lengthVector(toesPos, endPos)

        pm.move(toesControl.ctrl.cv, [0, 0, toesLength], relative=True)

        pm.addAttr(toesControl.ctrl, ln='SHAPE', at='enum',
                   enumName='___________',
                   k=True)
        toesControl.ctrl.SHAPE.setLocked(True)
        pm.addAttr(toesControl.ctrl, longName='curl', at='float', k=True, min=-10,
                   max=10, dv=0)
        pm.addAttr(toesControl.ctrl, longName='curlThumb', at='float', k=True, min=-10,
                   max=10, dv=0)
        pm.addAttr(toesControl.ctrl, longName='splay', at='float', k=True, min=-10,
                   max=10, dv=0)


        '''
        if side == 'l':
            pm.move(toesControl.ctrl.cv, [0, 0, toesLength], relative=True)
        else:
            pm.move(toesControl.ctrl.cv, [0, 0, toesLength * -1], relative=True)
        '''

        # make reverse ankle ik setup
        pm.parent( footBIK, legSkeletonParts  )
        footBReverseJnt = rig_transform(0, name=side + '_footB'+prefix+'Reverse', type='joint',
                                parent=legSkeletonParts, target=footBIK).object
        ankleReverseJnt = rig_transform(0, name=side + '_ankle'+prefix+'Reverse', type='joint',
                                parent=legSkeletonParts, target = footIK).object
        pm.parent( ankleReverseJnt, footBReverseJnt )
        ankleIK = rig_ik( side+'_ankle'+prefix ,footBReverseJnt, ankleReverseJnt, 'ikRPsolver' )
        #pm.parent(ankleIK.handle, module.parts)
        pm.hide(ankleIK.handle)
        pm.parent(ankleIK.handle, footToesControl.con)
        anklePV = rig_transform(0, name=side + '_anklePV'+prefix, type='locator',
                                parent=module.parts, target=footBallControl.con).object
        pm.move(anklePV, [50, 0, 0],relative=True, objectSpace=True)
        pm.parentConstraint( footToesControl.con, anklePV, mo=True )
        pm.poleVectorConstraint(anklePV, ankleIK.handle)
        pm.pointConstraint( footControl.con, ankleIK.handle, mo=True )
        pm.parentConstraint( footToesControl.con,footBReverseJnt,mo=True )

        pm.pointConstraint(ankleReverseJnt, ik.handle, mo=True)
        pm.orientConstraint( ankleReverseJnt, footIK, mo=True )

        # make leg aim
        legAimLoc = rig_transform(0, name=name+'FootAim', type='locator',
                                    parent=module.parts).object
        footAimLoc = rig_transform(0, name=side + '_footLeg'+prefix+'Aim', type='locator',
                                parent=module.parts).object

        pm.pointConstraint( self.legTop, legAimLoc  )
        pm.delete(pm.pointConstraint( footBallControl.con, footAimLoc ))
        pm.pointConstraint( footToesControl.con, footAimLoc,mo=True  )
        pm.setAttr( footAimLoc+'.rotateZ', -90 )
        pm.setAttr(legAimLoc+'.rotateZ', -90)

        legAimTop = mm.eval('rig_makePiston("'+legAimLoc+'", "'+footAimLoc+'", "'+name+'Aim");')

        #legAimMod = rig_transform(0, name=side + '_legFootAimModify', type='group',
         #                           parent=side+'_footLegAim_LOC', target=side+'_footLegAim_LOC').object

        #pm.parent( side+'_footLegAim_JNT', legAimMod )

        pm.parent( legAimTop, module.parts )

        # make foot ankle aim
        ankleAimLoc = rig_transform(0, name=side + '_ankleLeg'+prefix+'Aim', type='locator',
                                parent=module.parts).object
        footBAimLoc = rig_transform(0, name=side + '_footB'+prefix+'Aim', type='locator',
                                    parent=module.parts).object

        pm.parentConstraint( footIK, ankleAimLoc  )
        pm.delete(pm.orientConstraint( footIK, footBAimLoc ))
        pm.pointConstraint( footBReverseJnt, footBAimLoc )
        #pm.setAttr( footAimLoc+'.rotateZ', -90 )
        #pm.setAttr(legAimLoc+'.rotateZ', -90)

        ankleAimTop = mm.eval('rig_makePiston("'+ankleAimLoc+'", "'+footBAimLoc+'", "'+side+'_ankle'+prefix+'Aim");')

        pm.parent( ankleAimTop, module.parts )
        pm.parentConstraint( side+'_ankleLeg'+prefix+'Aim_JNT', footBIK, skipRotate=('x','y','z'), mo=True )
        pm.parentConstraint( footToesControl.con, footBIK, skipTranslate=('x','y','z'), mo=True )

        # make ankle bend
        startMeasure = rig_transform(0, name=name+'FullStart', type='locator',
                                  parent=module.parts, target=leg).object
        endMeasure = rig_transform(0, name=name+'FullEnd', type='locator',
                                  parent=module.parts, target=footToesControl.con).object
        totalLegDist = rig_measure(name=name+'FullLength', start=startMeasure, end=endMeasure,
                            parent=module.parts)

        legDistGlobal_MD = multiDivideNode( name+'_distanceRotationGlobal', 'multiply',
                        'rig_GRP', 'worldScale', '', totalLegDist.distanceVal )
        legDist_MD = multiDivideNode( name+'_distanceRotation', 'divide',
                        totalLegDist.distance, 'distance', legDistGlobal_MD, 'outputX' )

        pm.pointConstraint( footBallControl.con, endMeasure, mo=True )
        pm.pointConstraint( self.pelvisConnection, startMeasure, mo=True )

        '''

        expression -e -s "float $outputX = multiplyDivide8.outputX; \n\nfloat $degrees = 0;\n\n$degrees = -1*atand(1.0-$outputX);\n\nl_footAim_JNT.rotateZ = $degrees*1.5;"  -o "" -ae 1 -uc all  l_legRotate_EXP;

        
        '''
        mm.eval('expression -o ("'+side+'_footLeg'+prefix+'Aim_JNT") -s ("float $outputX = '+legDist_MD+'.outputX; float $degrees = 0;$degrees = -1*atand(1.0-$outputX);ry = $degrees*1.5;") -n ("'+name+'Rotate_EXP") -ae 1 -uc all ;')

        footOrientLoc = rig_transform(0, name=side+'_footOrient'+prefix, type='locator',
                                  parent=side+'_footLeg'+prefix+'Aim_JNT', target=footControl.con).object
        pm.setAttr( footOrientLoc+'.tx', 0)
        pm.setAttr( footOrientLoc+'.ty', 0)
        pm.setAttr( footOrientLoc+'.tz', 0)
        con = pm.parentConstraint( footControl.offset, footOrientLoc, footControl.modify[0], mo=True )
        pm.parentConstraint( name+'FootAim_JNT', side+'_footLeg'+prefix+'Aim_JNT', autoPVOffset, mo=True )

        
        # create ik stretchy and soft pop
        endBlendLoc = rig_ikStretchySoftPop(side, name, chainIK, module, footControl,
                                            ctrlSizeQuarter,
                                            self.legTop)

        #pm.pointConstraint(endBlendLoc, footToesControl.offset, mo=True)

        pm.addAttr(footBallControl.ctrl, ln='ikSettings', at='enum',
                 enumName='___________',
                 k=True)
        footBallControl.ctrl.ikSettings.setLocked(True)

        pm.addAttr( footBallControl.ctrl, longName='ikStretch', shortName='iks',attributeType="double",
                                min=0, max=1, defaultValue=0, keyable=True )
        pm.addAttr( footBallControl.ctrl, longName='midSlide', shortName='es',attributeType="double",
                                    min=-1, max=1, defaultValue=0, keyable=True )
        pm.addAttr( footBallControl.ctrl, longName='ankleStiffness', shortName='aksti',attributeType="double",
                                    min=0, max=1, defaultValue=0.5, keyable=True )

        targets = con.getWeightAliasList()
        pm.connectAttr( footBallControl.ctrl.ankleStiffness, targets[0] )
        connectReverse( name=name+'_ankleOrient_reverseNode#', input=(targets[0],0,0), output=(targets[1],0,0) )

        pm.connectAttr( footBallControl.ctrl.ikStretch, footControl.ctrl.ikStretch)
        pm.connectAttr( footBallControl.ctrl.midSlide, footControl.ctrl.midSlide)
        pm.setAttr( footControl.ctrl.ikSettings, k=False, cb=False )
        pm.setAttr( footControl.ctrl.ikStretch, k=False, cb=False )
        pm.setAttr( footControl.ctrl.ikSoftBlend, k=False, cb=False )
        pm.setAttr( footControl.ctrl.midSlide, k=False, cb=False )

        # create fk
        print 'fk chain ' + str(chainFK)
        fkCtrls = fkControlChain(chainFK, scale=ctrlSize)
        for fk in fkCtrls:
            pm.parent(fk.offset, module.controls)
            pm.setDrivenKeyframe(fk.offset + '.visibility',
                                 cd=module.top.ikFkSwitch,
                                 dv=1,
                                 v=0)
            pm.setDrivenKeyframe(fk.offset + '.visibility',
                                 cd=module.top.ikFkSwitch,
                                 dv=0,
                                 v=1)
        kneeFk = fkCtrls[1]
        '''
        rotateAxis = ['rx', 'ry', 'rz']
        if self.elbowAxis in rotateAxis: rotateAxis.remove(self.kneeAxis)
        for at in rotateAxis:
            kneeFk.ctrl.attr(at).setKeyable(False)
            kneeFk.ctrl.attr(at).setLocked(True)
        '''

        self.legControls['fk'] = fkCtrls

        self.connectIkFkSwitch(chains=[chainResult, chainIK, chainFK],
                               module=module, name=name)

        # constrain result to skeleton
        for i in range(0, len(chain)):
            pm.parentConstraint(chainResult[i], chain[i], mo=True)

        cmds.dgdirty(allPlugs=True)
        cmds.refresh()

        return module

    def foot(self, side = '', axis = 'ry', ctrlSize = 1.0, baseLimit=0.2):
        abc = list(string.ascii_lowercase)

        name = side + '_toes'
        sideName = side + '_'
        if side == '':
            name = 'toes'
            sideName = ''

        module = rig_module(name)
        self.fingersModule = module

        ctrlSizeHalf = [ctrlSize / 2.0, ctrlSize / 2.0, ctrlSize / 2.0]
        ctrlSize = [ctrlSize, ctrlSize, ctrlSize]

        rotateAxis = ['rx', 'ry', 'rz']

        rotateAxis.remove(axis)

        skipAxis = rotateAxis + ['tx', 'ty', 'tz']

        for toes in ( self.toeThumb, self.toeIndex, self.toeMid, self.toeRing,
                        self.toePinky ):

            toe = toes

            if side != '':
                toe = side + '_' + toe

            print 'toe is ' + toe
            if pm.objExists(toe):

                chainFingers = rig_chain(toe)

                childrenFngs = chainFingers.chainChildren

                childrenFngs.pop(len(childrenFngs) - 1)

                sc = simpleControls(toe,
                                    modify=2, scale=ctrlSize,
                                    parentOffset=module.controls)

                toeCtrl = sc[toe]
                #baseLimit = 0.2
                pm.transformLimits(toeCtrl.ctrl, tx=(-1 * baseLimit, baseLimit), etx=(1, 1))
                pm.transformLimits(toeCtrl.ctrl, ty=(-1 * baseLimit, baseLimit), ety=(1, 1))
                pm.transformLimits(toeCtrl.ctrl, tz=(-1 * baseLimit, baseLimit), etz=(1, 1))

                pm.move(toeCtrl.ctrl.cv, [0, 0, 1], relative=True)

                if 'Thumb' in toe:
                    if pm.objExists(sideName + 'footJA_JNT'):
                        pm.parentConstraint(sideName + 'footJA_JNT', toeCtrl.offset, mo=True)
                else:
                    if pm.objExists(sideName + 'footJB_JNT'):
                        pm.parentConstraint(sideName + 'footJB_JNT', toeCtrl.offset, mo=True)
                        if pm.objExists(sideName+'footToesOrient_LOC'):
                            pm.orientConstraint(sideName+'footToesOrient_LOC', toeCtrl.modify[0], mo=True,
                                                skip='x')

                        else:
                            orientLoc = rig_transform( 0, name=sideName+'footToesOrient',
                                                       type='locator',
                                           target=side+'_toesJA_JNT',
                                           parent=side+'_toesJA_JNT').object
                            pm.delete(pm.orientConstraint( toeCtrl.modify[0], orientLoc ))
                            pm.orientConstraint(orientLoc, toeCtrl.modify[0],
                                                mo=True,
                                                skip='x')

                pm.setAttr( toeCtrl.modify[0]+".rotateOrder", 2 )

                sc = simpleControls(childrenFngs,
                               modify=2, scale=ctrlSize,
                               parentOffset=module.controls,
                               lockHideAttrs=skipAxis)

                # fk control
                toesControl = self.legControls['toes'].ctrl
                if 'Thumb' in toe:
                    if pm.objExists(toesControl.curlThumb):
                        for key in sc:
                            control = sc[key]
                            rig_animDrivenKey(toesControl.curlThumb, (-10, 0, 10),
                                              control.modify[0] + '.rotateY', (-90, 0, 90 ))

                        rig_animDrivenKey(toesControl.curlThumb, (-10, 0, 10),
                                          toeCtrl.modify[1] + '.rotateY', (-90, 0, 90 ))
                else:
                    if pm.objExists( toesControl.curl ):
                        for key in sc:
                            control = sc[key]
                            rig_animDrivenKey(toesControl.curl, (-10, 0, 10),
                                              control.modify[0] + '.rotateY', (-90, 0, 90 ))
                            # move up toe control
                            if side == 'l':
                                pm.move(control.ctrl.cv, [5, 0, 0],os=True, relative=True,wd=True)
                            else:
                                pm.move(control.ctrl.cv, [-5, 0, 0],os=True, relative=True,wd=True)

                        rig_animDrivenKey(toesControl.curl, (-10, 0, 10),
                                          toeCtrl.modify[1] + '.rotateY', (-90, 0, 90 ))

                        # move up toe control
                        if side == 'l':
                            pm.move(toeCtrl.ctrl.cv, [5, 0, 0],os=True, relative=True,wd=True)
                        else:
                            pm.move(toeCtrl.ctrl.cv, [-5, 0, 0],os=True, relative=True,wd=True)

                pm.parent(toe, module.skeleton)

            else:
                print toe + ' does not exist...Skipping.'

        cmds.dgdirty(allPlugs=True)
        cmds.refresh()

        return module


def rig_quadPrepare():

    fngJoints = cmds.ls('*fng*JA_JNT')
    for digit in fngJoints:
        try:
            cmds.parent( digit, w=True)
        except ValueError:
            print 'Skipping ' + digit + ' as it does not exist'

    toesJoints = cmds.ls('*toe*JA_JNT')
    if 'l_toesJA_JNT' in toesJoints: toesJoints.remove('l_toesJA_JNT')
    if 'r_toesJA_JNT' in toesJoints: toesJoints.remove('r_toesJA_JNT')
    for digit in toesJoints:
        try:
            cmds.parent(digit, w=True)
        except ValueError:
            print 'Skipping ' + digit + ' as it does not exist'



    sideJointList = [ 'clavicleJA_JNT', 'armJA_JNT', 'legJA_JNT' ]
    for jnt in sideJointList:
        for side in ('l_', 'r_'):
            try:
                cmds.parent(side + jnt, w=True)
            except ValueError:
                print 'Skipping '+side+jnt+' as it does not exist'

    try:
        cmds.parent( 'headJA_JNT', w=True)
    except ValueError:
        print 'Skipping neckJA_JNT as it does not exist'

    try:
        cmds.parent( 'neckJA_JNT', w=True)
        lastNeckJnt = cmds.listRelatives('neckJA_JNT', typ='joint', ad=True)[0]
        neckEndJnt = rig_transform(0, name='neckJEnd', type='joint',
                                  target='headJA_JNT', parent=lastNeckJnt,
                                  rotateOrder=2).object
    except ValueError:
        print 'Skipping neckJA_JNT as it does not exist'

def rig_quadFinalize():

    try:
        # world space hands and feet
        for s in ['l', 'r']:
            pm.setAttr(s+'_foot_CTRL.space', 3)
            pm.setAttr(s+'_hand_CTRL.space', 1)
    except:
        pass



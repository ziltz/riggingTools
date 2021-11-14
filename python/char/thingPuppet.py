__author__ = 'Jerry'

import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mm

from create.rig_puppet import puppet
from create.rig_quadruped import *
from create.rig_biped import *

from make.rig_tail import *

from rutils.rig_anim import *

import string

'''

# puppet build
import char.thingPuppet as charPuppet
reload(charPuppet)
charPuppet.build()

charPuppet.buildScene()

TODO:
- neck joints
- blendshape facial
- fix hands and skinning
- switch tail off geometry
- legs ik? 

'''

def buildScene():
    puppet( character='thing',buildInScene=1 )

def build():
    puppet( character='thing' )
    #puppet( character='thing', rigBound = 'C:/Users/Jerry/Documents/maya/projects/thing/scenes/rigBound/thing_new_leg8.ma' )


def thingPrepareRig():
    print 'Prepare thing'

    rig_quadPrepare()


def thingRigModules():
    print 'Create thing rig modules'

    quad = rig_quadruped()
    biped = rig_biped()

    quad.spine(ctrlSize=40)
    biped.spineFullBodyCtrl = quad.spineFullBodyCtrl

    print biped.spineFullBodyCtrl.con

    quad.pelvis(ctrlSize=40)

    #headMod = quad.head(ctrlSize=30)

    '''
    constrainObject('headModify1_GRP',
                        ['neckJEnd_JNT','spineJF_JNT', 'spineJA_JNT', 'worldSpace_GRP'],
                        'head_CTRL', ['neck', 'chest', 'pelvis', 'world'],
                        spaceAttr='spaceOri',
                        type='orientConstraint')
    '''
    biped.neck( ctrlSize=20 )

    biped.head(ctrlSize=30)
    print biped.headCtrl
    pm.addAttr(biped.headCtrl.ctrl, ln='SHAPE', at='enum',
                   enumName='___________',
                   k=True)
    for shape in ('angry','joy','doubleHead','closed'):
        pm.addAttr(biped.headCtrl.ctrl, longName=shape,
                         attributeType="double",
                         min=0, max=10, defaultValue=0, keyable=True)
        rig_animDrivenKey(biped.headCtrl.ctrl.attr(shape), (0,10), 'blendshape_LOC.'+shape, (0,1))


    for side in ['l', 'r']:

        armModule = quad.arm(side, ctrlSize = 20)

        handModule = quad.hand(side, ctrlSize = 5)

        pm.delete(pm.listRelatives(side+'_fngThumbOffset_GRP', type='constraint'))
        pm.delete(pm.listRelatives(side+'_fngIndOffset_GRP', type='constraint'))
        pm.delete(pm.listRelatives(side+'_fngPnkyOffset_GRP', type='constraint'))
        cmds.parentConstraint(side+'_handJB_JNT', side+'_fngThumbOffset_GRP', mo=True )
        cmds.parentConstraint(side+'_handJB_JNT', side+'_fngIndOffset_GRP', mo=True )
        cmds.parentConstraint(side+'_handJB_JNT', side+'_fngPnkyOffset_GRP', mo=True )

        shoulderModule = quad.shoulder(side, ctrlSize = 10)

        # make quadruped leg 
        quad.legName = 'legSmallJA_JNT'
        quad.kneeName = 'kneeSmallJA_JNT'
        quad.footName = 'footSmallJA_JNT'
        quad.footBName = 'footSmallJB_JNT'
        quad.toesName = 'toesSmallJA_JNT'
        legSmallModule = quad.leg(side, ctrlSize = 15, doRolls=0, prefix='Small')

        quad.connectLegPelvis() 

        # make quadruped leg 
        quad.legName = 'legJA_JNT'
        quad.kneeName = 'kneeJA_JNT'
        quad.footName = 'footJA_JNT'
        quad.footBName = 'footJB_JNT'
        quad.toesName = 'toesJA_JNT'
        legModule = quad.leg(side, ctrlSize = 15, doRolls=0)

        quad.connectLegPelvis() 

    tail = rig_tail( 
                        name = 'tail' , 
                        rootJoint = 'tailJA_JNT', 
                        parent ='pelvisJA_JNT' ,
                        parentName = 'pelvis',
                        spine ='spineFullBodyCon_GRP',
                        ctrlSize = 5,
                        numIKCtrls = 8,
                        numFKCtrls = 8,
                        makeLag = 0, 
                        makeDynamic = 0 )
    tail.make()

    for side in ('l', 'r'):
        sideTail = rig_tail( 
                        name = side+'_tail' , 
                        rootJoint = side+'_tailJA_JNT', 
                        parent ='pelvisJA_JNT' ,
                        parentName = 'pelvis',
                        spine ='spineFullBodyCon_GRP',
                        ctrlSize = 5,
                        numIKCtrls = 8,
                        numFKCtrls = 8,
                        makeLag = 0, 
                        makeDynamic = 0 )
        sideTail.make()

def thingFinish():
    print 'Finishing thing'

    rig_quadFinalize()

    #cmds.parent('neckJEnd_headOffset_GRPProxyspace_LOC', 'spineJF_JNT')
    cmds.parent('r_toesSmallJA_JNT','r_footSmallJB_JNT')
    cmds.parent('l_toesSmallJA_JNT','l_footSmallJB_JNT')

    #pivots
    cmds.setAttr("l_footBallSmallPivot_CTRL.translateY", -9.368)
    cmds.setAttr("r_footBallSmallPivot_CTRL.translateY", -9.368)
    cmds.setAttr("r_footBallPivot_CTRL.translateY",-8.025)
    cmds.setAttr("l_footBallPivot_CTRL.translateY", -8.025)
    cmds.setAttr("r_footBallPivot_CTRL.translateZ", -0.834)
    cmds.setAttr("l_footBallPivot_CTRL.translateZ", -0.834)

    pm.move( 'tailUpperAim_LOCUp', 0, 1000, 0,r=True,os=True )
    pm.move('tailLowerAim_LOCUp', 0, 1000, 0, r=True, os=True)
    
    hideObjs = ['l_toesSmallModify1_GRP','r_toesSmallModify1_GRP','r_fingModify1_GRP','l_fingModify1_GRP','l_footToesSmallModify1_GRP','r_footToesSmallModify1_GRP',
                'l_footToesModify1_GRP','l_toesModify1_GRP','r_footToesModify1_GRP','r_toesModify1_GRP', 'tailTipIKOffset_GRP', 'r_tailTipIKOffset_GRP', 'l_tailTipIKOffset_GRP']
    for obj in hideObjs:
        cmds.setAttr(obj+'.v', 0)

    for obj in cmds.ls('*tailMid*IKOffset_GRP'):
        cmds.setAttr(obj+'.v', 0)

    cmds.connectAttr('displayModulesToggleControl.tail', 'vis_LOC.tail',f=True)
    cmds.connectAttr('displayModulesToggleControl.l_tail', 'vis_LOC.lTail',f=True)
    cmds.connectAttr('displayModulesToggleControl.r_tail', 'vis_LOC.rTail',f=True)
    cmds.setAttr("displayModulesToggleControl.tail", 0)
    cmds.setAttr("displayModulesToggleControl.l_tail", 0)
    cmds.setAttr("displayModulesToggleControl.r_tail", 0)

    pm.move(pm.PyNode( 'tailFKA_CTRL.cv[:]'), 0 , 10.7, 0, r=True, os=True)
    pm.move(pm.PyNode( 'spineFullBody_CTRL.cv[:]'), 0 , 26.5, -21.3, r=True, os=True)
    displayShapes = pm.PyNode( 'displayModulesToggleControl').getShapes()
    for shape in displayShapes:
        pm.move(pm.PyNode( shape+'.cv[:]'), 0 , -100, 0, r=True, os=True)

    pm.scale(pm.PyNode( 'l_foot_CTRL.cv[:]'), 1.6 , 1.6, 1.6)
    pm.scale(pm.PyNode( 'r_foot_CTRL.cv[:]'), 1.6 , 1.6, 1.6)

    pm.scale(pm.PyNode( 'pelvis_CTRL.cv[:]'), 1.3 , 1, 1, r=True, ocp=True)


    controlSet = pm.PyNode('thingRigPuppetControlSet')
    '''
    for s in ('l', 'r'):
        controlSet.removeMembers([ s+'_shoulder_CTRL' ])
    '''    












__author__ = 'Jerry'

import maya.cmds as mc
import pymel.core as pm
import maya.mel as mm

from create.rig_puppet import puppet
from create.rig_biped import *
from create.rig_facial import *
from create.rig_quadruped import *

from make.rig_tail import *
from make.rig_controls import *
from make.rig_flex import *

from rutils.rig_nodes import *

import string

'''

# puppet build
import char.elephantPuppet as charPuppet
reload(charPuppet)
charPuppet.build()

charPuppet.buildScene()

'''

def buildScene():
    puppet( character='elephant',buildInScene=1 )

def build():
    puppet( character='elephant' )
    #puppet( character='elephant', rigBound = 'C:/Users/Jerry/Documents/maya/projects/elephant/scenes/rigBound/elephant_new_leg8.ma' )


def elephantPrepareRig():
    print 'Prepare elephant'

    rig_quadPrepare()


def elephantRigModules():
    print 'Create elephant rig modules'

    quad = rig_quadruped()

    quad.spine(ctrlSize=100)

    quad.pelvis(ctrlSize=60)

    neckMod = quad.neck(ctrlSize=30, 
                splinePosList=[ 'neckStart_LOC', 'neckMidA_LOC', 'neckMidB_LOC', 'neckEnd_LOC'])

    headMod = quad.head(ctrlSize=60)

    # jaw control
    jawControl = rig_control(name='jaw', shape='circle', scale=(40,40,40),
                             lockHideAttrs=['rx'],
                             parentOffset=headMod.controls, colour='white')

    pm.rotate(jawControl.ctrl.cv, -90, 0, 0, r=True, os=True)
    pm.move(jawControl.ctrl.cv, 2, 0, 0, r=True, os=True)

    pm.delete(pm.parentConstraint( 'jawJA_JNT' ,jawControl.offset))
    pm.parentConstraint('headJA_JNT', jawControl.offset, mo=True)
    pm.parentConstraint(jawControl.con, 'jawJA_JNT', mo=True)
    jawPos = pm.xform('jawJA_JNT', translation=True, query=True, ws=True)
    jawEndPos = pm.xform( 'jawJEnd_JNT', translation=True, query=True, ws=True)
    jawLength = lengthVector(jawPos, jawEndPos)
    pm.move(pm.PyNode(jawControl.ctrl + '.cv[:]'), jawLength/2,0, 0, r=True, os=True)

    
    for side in ['l', 'r']:

        armModule = quad.arm(side, ctrlSize = 60)

        handModule = quad.hand(side, ctrlSize = 30)

        shoulderModule = quad.shoulder(side, ctrlSize = 30)

        # make quadruped leg 
        legModule = quad.leg(side, ctrlSize = 70)

        toesModule = quad.foot(side, ctrlSize=7, baseLimit=1)

        quad.connectLegPelvis()

    tail = rig_tail( rootJoint = 'tailJA_JNT',
                        numIKCtrls = 4, 
                        numFKCtrls = 4,  
                        ctrlSize = 10,
                        makeDynamic = 0 )
    tail.make()

    if pm.objExists('tailDynJA_JNT'):
        pm.parent('tailDynJA_JNT', 'pelvisJA_JNT')

    trunk = rig_tail(   name = 'trunk',
                        rootJoint = 'trunkJA_JNT',
                        parent = 'headJA_JNT',
                        parentName = 'head',
                        numIKCtrls = 6, 
                        numFKCtrls = 6,  
                        ctrlSize = 15,
                        makeLag = 0,
                        makeDynamic = 0 )
    trunk.make()


def elephantFinish():
    print 'Finishing elephant'

    rig_quadFinalize()

    '''
    pm.setAttr("neckFocus_CTRL.focusNeck", 0.75)

    pm.setAttr("spineUpperPivot_CTRL.translateY", -17.164)
    pm.setAttr("spineUpperPivot_CTRL.translateZ", 1.81)
    pm.setAttr("spineUpper_CTRL.stretch", 0.2)
    '''
    pm.move( 'tailUpperAim_LOCUp', 0, 1000, 0,r=True,os=True )
    pm.move('tailLowerAim_LOCUp', 0, 1000, 0, r=True, os=True)

    pm.move(pm.PyNode( 'neckTipIK_CTRL.cv[:]'), 0 , 0, -5, r=True, os=True)
    pm.move(pm.PyNode( 'neckMidBIK_CTRL.cv[:]'), 0 ,-8.5, -13, r=True, os=True)
    pm.move(pm.PyNode( 'neckMidAIK_CTRL.cv[:]'), 0 , -1 , -23, r=True, os=True)
    
    controlSet = pm.PyNode('elephantRigPuppetControlSet')
    for s in ('l', 'r'):
        #pm.setAttr("displayModulesToggleControl."+s+"_fingers", 0)
        #pm.setAttr("displayModulesToggleControl."+s+"_toes", 0)

        #pm.setAttr(s+"_armPV_CTRL.space", 1)
        #pm.setAttr(s+"_shoulder_CTRL.followArm", 1)

        #pm.rotate(pm.PyNode(s+'_handBall_CTRL').cv, 0, 90, 0, r=True, os=True)
        #pm.scale(pm.PyNode(s+'_handBall_CTRL').cv, 2, 2, 2)

        #pm.parentConstraint( s+'_anklePos_JNT', s+'_toeThumbModify1_GRP' ,mo=True )

        controlSet.removeMembers([ s+'_shoulder_CTRL' ])
        












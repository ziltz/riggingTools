import maya.cmds as cmds
import math

## TIME : 05/05/2014 02:52

global_armLoc_list = []
global_armPConstraint_list = []
global_joints_groupList= []

def global_ctrl():
    globalCtrl = cmds.curve(n=prefixName+"global_ctrl",d=1,p=[(-1.8975,0,0),(-1.4025,0,0.37125),(-1.4025,0,0.12375),(-0.380966,0,0.157801),(-1.079222,0,0.904213),(-1.254231,0,0.729204),(-1.341735,0,1.341735),(-0.729204,0,1.254231),(-0.904213,0,1.079222),(-0.157801,0,0.380966),(-0.12375,0,1.4025),(-0.37125,0,1.4025),(0,0,1.8975),(0.37125,0,1.4025),(0.12375,0,1.4025),(0.157801,0,0.380966),(0.904213,0,1.079222),(0.729204,0,1.254231),(1.341735,0,1.341735),(1.254231,0,0.729204),(1.079222,0,0.904213),(0.380966,0,0.157801),(1.4025,0,0.12375),(1.4025,0,0.37125),(1.8975,0,0),(1.4025,0,-0.37125),(1.4025,0,-0.12375),(0.380966,0,-0.157801),(1.079222,0,-0.904213),(1.254231,0,-0.729204),(1.341735,0,-1.341735),(0.729204,0,-1.254231),(0.904213,0,-1.079222),(0.157801,0,-0.380966),(0.12375,0,-1.4025),(0.37125,0,-1.4025),(0,0,-1.8975),(-0.37125,0,-1.4025),(-0.12375,0,-1.4025),(-0.157801,0,-0.380966),(-0.904213,0,-1.079222),(-0.729204,0,-1.254231),(-1.341735,0,-1.341735),(-1.254231,0,-0.729204),(-1.079222,0,-0.904213),(-0.380966,0,-0.157801),(-1.4025,0,-0.12375),(-1.4025,0,-0.37125),(-1.8975,0,0)],k=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48])
    cmds.makeIdentity(apply=True,t=1,r=1,s=1,n=0)
    return globalCtrl

def IKFK_ctrl():
    switchNme = getTextBox_text(ikfk_switchName)
    ctrl = cmds.curve(n=prefixName+switchNme+"_IK_FK_Switch_ctrl",d=3,p=[(-1.508537,0,0),(-1.059622,0,-0.316884),(-0.161791,0,-0.950653),(-0.231491,0,-0.132891),
                     (0.0199252,0,0.0238494),(0.843595,0,-0.46025),(1.7044,0,-1.130663),(1.00832,0,-0.442815),(0.512875,0,-0.0222687),
                     (1.031578,0,0.508979),(1.701544,0,1.119434),(0.831393,0,0.447942),(0.018681,0,0.000680685),(-0.212893,0,0.0475119),
                     (-0.15231,0,0.973132),(-1.056461,0,0.324377),(-1.508537,0,0)],k=[0,0,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,14,14])
    cmds.rotate( 0,0,-90, r=True, os=True)
    cmds.rotate( 90,0,0, r=True, os=True )
    cmds.makeIdentity(apply=True,t=1,r=1,s=1,n=0)
    cmds.select(clear=True)
    return ctrl

def ikCtrl():
    switchNme = getTextBox_text(ikfk_switchName)
    ctrl = cmds.curve(n=prefixName+switchNme+"_ik_ctrl",d=1,p=[(0.5,0.5,0.5),(0.5,0.5,-0.5),(-0.5,0.5,-0.5),(-0.5,-0.5,-0.5),(0.5,-0.5,-0.5),
                      (0.5,0.5,-0.5),(-0.5,0.5,-0.5),(-0.5,0.5,0.5),(0.5,0.5,0.5),(0.5,-0.5,0.5),(0.5,-0.5,-0.5),(-0.5,-0.5,-0.5),
                      (-0.5,-0.5,0.5),(0.5,-0.5,0.5),(-0.5,-0.5,0.5),(-0.5,0.5,0.5)],k=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
    cmds.makeIdentity(apply=True,t=1,r=1,s=1,n=0)
    return ctrl
    
def ikPVCtrl():
    switchNme = getTextBox_text(ikfk_switchName)
    ctrl = cmds.curve(n=prefixName+switchNme+'_ik_poleVector_loc',d=1,p=[(0,2,0),(1,0,-1),(-1,0,-1),(0,2,0),(-1,0,1),(1,0,1),(0,2,0),(1,0,-1),(1,0,1),(-1,0,1),
                                            (-1,0,-1)],k=[0,1,2,3,4,5,6,7,8,9,10])                                    
    cmds.makeIdentity(apply=True,t=1,r=1,s=1,n=0) 
    return ctrl
    
def ikPVCtrl2():
    switchNme = getTextBox_text(ikfk_switchName)
    ctrl = cmds.curve(n=prefixName+switchNme+'_ik_poleVector_loc',d=1,p=[(0,0,1),(0,0,-1),(0,2,0),(0,-2,0),(0,0,-1),(2,0,0),(-2,0,0),(0,0,-1)],k=[0,1,2,3,4,5,6,7])
    cmds.rotate( 0,-90,0, r=True, os=True)
    cmds.makeIdentity(apply=True,t=1,r=1,s=1,n=0)
    cmds.select(clear=True)
    return ctrl
    
def displayLocalAxes():
    print 'hey'
    jointList = []
    firstJoint = getTextBox_text(jointTextBox)
    if not firstJoint:
        cmds.confirmDialog( title='Error', message='Error: Please click on "Get Joint" button to specify joint name', 
                    button=['Ok'])
        print 'Error: Please click on "Get Joint" button to specify joint name'
    else:
        jointList.append(firstJoint)
        firstJoint_children = getChildren( firstJoint, 'joint' )
        #print firstJoint_children
        if firstJoint_children:
            for i in range(1, len(firstJoint_children)+1):
                jointList.append( getLastItem(firstJoint_children, i) )
            
        for jnts in jointList:
            toggleAxisSwitch = cmds.getAttr(jnts+'.displayLocalAxis' )
            if toggleAxisSwitch == 1:  
                cmds.setAttr( jnts+'.displayLocalAxis', 0 )
            else:
                cmds.setAttr( jnts+'.displayLocalAxis', 1 )
    
def getLastItem( _list, _inc ):
    if _inc >= 1 and _inc <= len( _list ):
        return _list[ len(_list) - _inc ]
    else:
        return 'Error : Out of Bounds'

def fillTextBox(_textField):
    if not cmds.ls(sl=True):
        cmds.confirmDialog( title='Error', message='Please select an object', 
                            button=['Ok'])
        print 'No Joint selected'
    else:
        cmds.textField( _textField, edit=True, text=cmds.ls(sl=True)[0] )

def getTextBox_text(_textField):
    textName =  cmds.textField( _textField, query=True, text=True ) 
    return textName

def getChildren( _joint, _type ):
    return cmds.listRelatives( _joint, ad=True, children=True, type=_type )

def createTempJointChain( ):
    setTempNaming()
    tempList = cmds.duplicate( getTextBox_text(jointTextBox) ) # duplicate joint chain
    return tempList

def setTempNaming():
    if cmds.namespace( exists='TEMP' ):
        print 'temp exists'
    else:
        cmds.namespace( add='TEMP' ) # create temp name space
        cmds.namespace( set='TEMP' ) # set temp name space
        
def setRootNaming() :    
    while cmds.namespace( exists=':TEMP' ):
        cmds.namespace( removeNamespace = ":TEMP", 
        mergeNamespaceWithRoot = True) # remove TEMP namespace
        
def renameJoints( _tempList, _typeJoint ):
    newJointList = []
    for jnt in _tempList: # iterate through joint chain and rename to ik/fk
        jntNme = jnt.replace( prefixName, prefixName+_typeJoint+'_')
        cmds.select(jnt)
        newJointList.append(cmds.rename(jntNme))
    
    return newJointList
    
def assignPrefixName():
    global prefixName
    prefixName = getTextBox_text(prefixText)
    if not prefixName:
        prefixName = 'godzilla'
        cmds.confirmDialog( title='Warning', 
                            message='The name defaultChar will be used instead as nothing was input the box, please type in the desired name in the textbox if you do not want to use defaultChar!', 
                            button=['Ok'])
        print 'defaultChar is used as prefixName'
        cmds.textField( prefixText, edit=True, text=prefixName )
    else:
        if cmds.objExists( prefixName+'_global_ctrl'):
            cmds.confirmDialog( title='Warning', 
                            message='Warning : This name is already in use.', 
                            button=['Ok'])
            print 'prefixname already in use'
        else:
            cmds.confirmDialog( title='Confirmation', 
                            message='The name you have chosen : '+prefixName, 
                            button=['Ok'])
            print 'prefixName is '+prefixName
    prefixName = prefixName+'_'
    
def orientJoints():
    if not getTextBox_text(jointTextBox):
        cmds.confirmDialog( title='Error', message='There is no root joint to orient. Please select a joint.', 
                            button=['Ok'])
        print 'There is no root joint to orient. Please select a joint.'
    else:
        orientJointChain = getTextBox_text(jointTextBox)
        cmds.joint( orientJointChain, e=True, sao='zup', oj='xyz', zso=True, children=True )

def mirrorJoints():
    if not getTextBox_text(jointTextBox):
        cmds.confirmDialog( title='Error', message='There is no root joint to mirror. Please select a joint.', 
                            button=['Ok'])
        print 'There is no root joint to mirror. Please select a joint.'
    else:
        mirrorJointChain = getTextBox_text(jointTextBox)
        cmds.mirrorJoint(mirrorJointChain, myz=True,mirrorBehavior=True,searchReplace=('_l_', '_r_') )

def lengthVector( posAx, posAy, posAz, posBx, posBy, posBz ):
    dx = posAx - posBx
    dy = posAy - posBy
    dz = posAz - posBz
    return math.sqrt( dx*dx + dy*dy + dz*dz )
   
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

def plusMinusNode( _nme, _operation, _inputNme1, _input1, _inputNme2, _input2 ):
    node = cmds.shadingNode('plusMinusAverage', asUtility=True)
    avgNode = cmds.rename(node, _nme+'_plusMinAvg')
    if not _inputNme1:
        cmds.setAttr( avgNode+'.input1D[0]', _input1 )
    else:
        cmds.connectAttr( _inputNme1+'.'+_input1 ,avgNode+'.input1D[0]', f=True )
        
    if not _inputNme2:
        cmds.setAttr( avgNode+'.input1D[1]', _input2 )
    else:
        cmds.connectAttr( _inputNme2+'.'+_input2 ,avgNode+'.input1D[1]', f=True )
        
    if _operation == 'sum':
        cmds.setAttr( avgNode+'.operation', 1 )
    else:
        cmds.setAttr( avgNode+'.operation', 2 )
    
    return avgNode
    

def globalFixNode( _nodeMDNme, _fixNode, _fixNodeAttr ):
    print 'START OF globalFixNode ---------------------------------'
    globalMDNode = multiDivideNode( _nodeMDNme, 'divide', _fixNode, _fixNodeAttr, globalCtrl, 'scaleX' )
    #cmds.connectAttr( _fixNode+'.'+_fixNodeAttr, globalMDNode+'.input1X', f=True )
    #cmds.connectAttr( globalCtrl+'.scaleX', globalMDNode+'.input2X', f=True )
    print 'END OF globalFixNode ---------------------------------'
    return globalMDNode

def createIkHandle( _name, _startJnt, _endJnt, _sol ):
    ikHndle = cmds.ikHandle( n=_name+'_ik_Handle', 
                            sj=_startJnt, ee=_endJnt,  sol=_sol) 
    cmds.select(ikHndle[0])   
    ikEffector = cmds.ikHandle( ee=True, query=True )
    cmds.rename( ikEffector, _name+'_ik_effector' )       
    cmds.setAttr( ikHndle[0]+'.visibility', 0 )          
    cmds.select(clear=True)
    return ikHndle
  
def createIkSplineTwist( startCtrl, endCtrl, ctrlObj, _ikHandle, axis):
 '''
 Create twist control for the spline IK setup
   
  startCtrl : node controlling the start of the joint chain
  endCtrl  : node controlling the end of the joint chain
  ctrlObj  : control object to host the twist attributes
  ikHandle : the spline IK handle
  axis  : the rotation axis for twisting on the controls : "x", "y", "z", "-x", "-y", "-z"
 '''
 # check nodes
 for node in [startCtrl, endCtrl, ctrlObj, _ikHandle]:
  if not cmds.objExists(node):
   cmds.error("%s does not exist." % node)
 # check axis
 if axis not in ["x", "y", "z", "-x", "-y", "-z"]:
  cmds.error("Invalid axis.")
   
 # check if our twist axis is on the negative side
 neg = False
 splitString = axis.split("-")
 if splitString[0] == "":
  axis = splitString[1]
  neg = True
 axis = ".r" + axis
  
 # create new attributes
 cmds.addAttr(ctrlObj, ln="autoTwist", at="double", dv=1, min=0, max=1, k=True)
 cmds.addAttr(ctrlObj, ln="twistOffset", at="double", dv=0, k=True)
   
 # create nodes for autoTwist and twistOffset
 autoTwist1 = cmds.createNode("multiplyDivide", n="md_" + ctrlObj + "_autoTwist1")
 autoTwist2 = cmds.createNode("multiplyDivide", n="md_" + ctrlObj + "_autoTwist2")
 twistOffset1 = cmds.createNode("plusMinusAverage", n="pma_" + ctrlObj + "_twistOffset1")
 twistOffset2 = cmds.createNode("plusMinusAverage", n="pma_" + ctrlObj + "_twistOffset2")
 
 # connect the end control
 cmds.connectAttr(endCtrl + axis, autoTwist1 + ".input1X")
 cmds.connectAttr(ctrlObj + ".autoTwist", autoTwist1 + ".input2X")
  
 cmds.connectAttr(autoTwist1 + ".outputX", twistOffset1 + ".input1D[0]")
 cmds.connectAttr(ctrlObj + ".twistOffset", twistOffset1 + ".input1D[1]")
  
 # connect the start control
 cmds.connectAttr(startCtrl + axis, autoTwist2 + ".input1X")
 cmds.connectAttr(ctrlObj + ".autoTwist", autoTwist2 + ".input2X")
 
 cmds.connectAttr(twistOffset1 + ".output1D", twistOffset2 + ".input1D[0]")
 cmds.connectAttr(autoTwist2 + ".outputX", twistOffset2 + ".input1D[1]")
  
 cmds.setAttr(twistOffset2 + ".operation", 2) # subtract
  
 # connect to the ikHandle
 cmds.connectAttr(startCtrl + axis, _ikHandle + ".roll")
 cmds.connectAttr(twistOffset2 + ".output1D", _ikHandle + ".twist")
  
 # make changes if the twist axis is on the negative side
 if neg:
  invTwist1 = cmds.createNode("multiplyDivide", n="md_" + ctrlObj + "_invTwist1")
  invTwist2 = cmds.createNode("multiplyDivide", n="md_" + ctrlObj + "_invTwist2")
   
  cmds.setAttr(invTwist1 + ".input2X", -1)
  cmds.setAttr(invTwist2 + ".input2X", -1)
   
  cmds.connectAttr(endCtrl + axis, invTwist1 + ".input1X")
  cmds.connectAttr(startCtrl + axis, invTwist2 + ".input1X")
   
  cmds.connectAttr(invTwist1 + ".outputX", autoTwist1 + ".input1X", f=True)
  cmds.connectAttr(invTwist2 + ".outputX", autoTwist2 + ".input1X", f=True)
  cmds.connectAttr(invTwist2 + ".outputX", _ikHandle + ".roll", f=True)
    
def createSDK( _driver, _driverAttr, _driven, _drivenAttr, 
               _driverValue1, _driverValue2, _drivenValue1, _drivenValue2):
    cmds.setAttr(_driver+'.'+_driverAttr, _driverValue1) # set driver value
    cmds.setAttr(_driven+'.'+_drivenAttr, _drivenValue1) # set driven value
    cmds.setDrivenKeyframe(_driven+'.'+_drivenAttr, cd=_driver+'.'+_driverAttr) # set SDK
    cmds.setAttr(_driver+'.'+_driverAttr, _driverValue2) # set driver value
    cmds.setAttr(_driven+'.'+_drivenAttr, _drivenValue2) # set driven value
    cmds.setDrivenKeyframe(_driven+'.'+_drivenAttr, cd=_driver+'.'+_driverAttr) # set SDK
    # set back to default values
    cmds.setAttr(_driver+'.'+_driverAttr, _driverValue1) # set driver value
    cmds.setAttr(_driven+'.'+_drivenAttr, _drivenValue1) # set driven value

def jointBlendColours( _switchNme, _transform, _ikList, _fkList, _mainList, _ikfkName, _switchAttrNme ):         
    for i in range(0,len(_mainList)):
        nme = prefixName+str(i)
        
        # bldColor for rotation
        bldColor = cmds.shadingNode('blendColors', asUtility=True)
        bldName = cmds.rename(bldColor, nme+"_"+_switchNme+'_'+_transform+"_bldColor")
        "Select ik, fk then bind joints in this order"
        cmds.connectAttr( _ikList[i]+'.'+_transform, bldName+'.color1', f=True ) # connect ik jnt to color1
        cmds.connectAttr( _fkList[i]+'.'+_transform, bldName+'.color2', f=True ) # connect fk jnt to color2
        cmds.connectAttr( bldName+'.output', _mainList[i]+'.'+_transform, f=True ) # connect bldColor output to bind jnt
        
        # IK = 0, FK = 10 on switch
        # IK bldColors = 1, FK bldColors = 0
        # driver name, driver attribute, driven name, driven attribute
        # driver first and second values, driven first and second values
        createSDK( _ikfkName, _switchAttrNme, bldName, 'blender', 
                    0, 10, 1, 0 )

def lockHide_attributes( _objNme, _translateAttr, _rotationAttr, _scaleAttr ):
    if _translateAttr == True:
        cmds.setAttr( _objNme+'.tx', channelBox=False, keyable=False, lock=True )
        cmds.setAttr( _objNme+'.ty', channelBox=False, keyable=False, lock=True )
        cmds.setAttr( _objNme+'.tz', channelBox=False, keyable=False, lock=True )
    if _rotationAttr == True:
        cmds.setAttr( _objNme+'.rx', channelBox=False, keyable=False, lock=True )
        cmds.setAttr( _objNme+'.ry', channelBox=False, keyable=False, lock=True )
        cmds.setAttr( _objNme+'.rz', channelBox=False, keyable=False, lock=True )
    if _scaleAttr == True:
        cmds.setAttr( _objNme+'.sx', channelBox=False, keyable=False, lock=True )
        cmds.setAttr( _objNme+'.sy', channelBox=False, keyable=False, lock=True )
        cmds.setAttr( _objNme+'.sz', channelBox=False, keyable=False, lock=True )
        
def getDistanceDimensions( _distLocList ):
    # create distance dimensions for measurement
    print '*** start of getDistanceDimensions function ***-------------------------'
    print 'getDistanceDimensions distLocList = '+str(_distLocList)
    locArm = _distLocList[0]
    locElbow = _distLocList[1]
    locWrist = _distLocList[2]
    
    print 'locArm = '+_distLocList[0]
    print 'locElbow = '+_distLocList[1]
    print 'locWrist = '+_distLocList[2]
    
    locArmDist = cmds.getAttr( locArm+'.translate' )
    locElbowDist = cmds.getAttr( locElbow+'.translate' )
    locWristDist = cmds.getAttr( locWrist+'.translate' )
    
    distDim1 = cmds.distanceDimension( startPoint=( locArmDist[0] ), endPoint=( locElbowDist[0] ))
    distDim2 = cmds.distanceDimension( startPoint=( locElbowDist[0] ), endPoint=( locWristDist[0] ))
    distDim3 = cmds.distanceDimension( startPoint=( locArmDist[0] ), endPoint=( locWristDist[0] ))
    
    distDim1 = cmds.rename( distDim1, locArm+'_upper_distanceDimensionShape' )
    cmds.select( distDim1 )
    distArmDim = cmds.pickWalk( direction='up' )
    distArm = cmds.rename( distArmDim, locArm+'_upper_distanceDimension' )
    
    distDim2 = cmds.rename( distDim2, locElbow+'_lower_distanceDimensionShape' )
    cmds.select( distDim2 )
    distElbowDim = cmds.pickWalk( direction='up' )
    distElbow = cmds.rename( distElbowDim, locElbow+'_lower_distanceDimension' )
    
    distDim3 = cmds.rename( distDim3, locWrist+'_ctrlDist_distanceDimensionShape' )
    cmds.select( distDim3 )
    distWristDim = cmds.pickWalk( direction='up' )
    distWrist = cmds.rename( distWristDim, locWrist+'_ctrlDist_distanceDimension' )
    
    cmds
    
    distanceDim_list = ( distArm, distElbow, distWrist )
    for dist in distanceDim_list:
        cmds.setAttr( dist+'.visibility', 0 )
        
    #cmds.group( distArm, distElbow, distWrist, n=prefixName+'distanceDimensions_grp' )
    # return the list
    print 'distanceDim_list is = '+str(distanceDim_list)
    print '*** end of getDistanceDimensions function ***-------------------------'
    
    return distanceDim_list

def createDistanceLocs( _jntList ):
    # create distance locators and return the list with names
    print '*** start of createDistanceLocs function ***-------------------------'
    print 'input joint list = '+str(_jntList)
    distanceLoc_list = []
    for jnt in _jntList:
        locName = jnt.replace("_jnt", "_distance_loc")
        loc = cmds.spaceLocator(n=locName)[0]
        cmds.delete(cmds.pointConstraint(jnt, loc, mo=False))
        cmds.delete(cmds.orientConstraint(jnt, loc, mo=False))
        cmds.setAttr( loc+'.visibility', 0 )
        distanceLoc_list.append(loc)
        print 'locator names = '+loc
        
    print '*** end of createDistanceLocs function ***-------------------------'
    return distanceLoc_list

def cleanUpLoc():
    if not global_armLoc_list:
        cmds.confirmDialog( title='Error', message='There are no locators to clear !', 
                            button=['Ok'])
        print 'There are no locators to clear !!!'
    else:
        if not cmds.objExists( str(global_armPConstraint_list[0]) ):
            for i in global_armPConstraint_list:
                cmds.delete( i ) # delete constraints
            for i in range(1, len(global_armLoc_list)+1):
                cmds.delete( getLastItem(global_armLoc_list, i) ) # delete arm locaters
            global_armPConstraint_list[:] = [] # clear constraint list
            global_armLoc_list[:] = [] # clear locater list
        else:
            cmds.confirmDialog( title='Error', message='There are no locators to clear !', 
                    button=['Ok'])
            print 'There are no locators to clear ! apparentely'
            global_armPConstraint_list[:] = [] # clear constraint list
            global_armLoc_list[:] = [] # clear locater list

def addStretchyIKJoints( _jntList, _distanceDim, _ikControl, _wristStretchDist ):
    print 'addStretchyIKJoints function starts here ------------------------'
    # assign appropriate names
    switchNme = getTextBox_text(ikfk_switchName)
    nme = prefixName+switchNme
    upperDistDim = _distanceDim[0]
    lowerDistDim = _distanceDim[1]
    ctrlDistDim = _distanceDim[2]
    armJnt = _jntList[0]
    elbowJnt = _jntList[1]
    handJnt = _jntList[2]
    wristStretchDist = _wristStretchDist[0]
    wristSoftBlendDist = _wristStretchDist[1]
    
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


def createShoulderJoints():
    if cmds.objExists(prefixName+'l_shoulder_jnt'):
        cmds.confirmDialog( title='Error', message='Warning: Object exists already! Please choose another name', 
                            button=['Ok'])
        print 'Warning Object exists already ! Choose another name'
    else:
        cmds.select(clear=True)
    
        shoulder_jnt = cmds.joint( name=prefixName+'l_shoulder_jnt')
        shoulderEnd_jnt = cmds.joint( name=prefixName+'l_shoulderEnd_jnt', p=[2.5,0,0] )
        cmds.joint( shoulder_jnt, e=True, sao='yup', oj='xyz',zso=True )
        
        locShoulder = cmds.spaceLocator(n=prefixName+'temp_shoulder_loc')[0]
        locShoulderEnd = cmds.spaceLocator(n=prefixName+'temp_shoulderEnd_loc')[0]
        cmds.delete(cmds.pointConstraint(shoulderEnd_jnt, locShoulderEnd, mo=False))
        global_armPConstraint_list.append(cmds.pointConstraint(locShoulder, shoulder_jnt, mo=False))
        global_armPConstraint_list.append(cmds.pointConstraint(locShoulderEnd, shoulderEnd_jnt, mo=False))
        global_armLoc_list.append( locShoulder )
        global_armLoc_list.append( locShoulderEnd )
        
        cmds.parent( locShoulderEnd, locShoulder )
        
def createArmJoints():
    nme = getTextBox_text(ikfk_switchName)
    nme = prefixName+nme
    if cmds.objExists(nme+'_l_start_jnt'):
        cmds.confirmDialog( title='Error', message='Warning: Object exists already! Please choose another name', 
                            button=['Ok'])
        print 'Warning Object exists already ! Choose another name'
    else:
        cmds.select(clear=True)
        
        arm_jnt = cmds.joint( name=nme+'_l_start_jnt')
        elbow_jnt = cmds.joint( name=nme+'_l_mid_jnt', p=[4,0,-2] )
        cmds.joint( arm_jnt, e=True, sao='yup', oj='xyz',zso=True )
        hand_jnt = cmds.joint( name=nme+'_l_end_jnt', p=[8,0,0] )
        cmds.joint( elbow_jnt, e=True, sao='yup', oj='xyz',zso=True )
        hand_end_jnt = cmds.joint( name=nme+'_l_visual_end_jnt', p=[9,0,1] )
        cmds.joint( hand_jnt, e=True, sao='yup', oj='xyz',zso=True )
        
        armJnt_list = [ arm_jnt, elbow_jnt, hand_jnt, hand_end_jnt ]
        armLoc_list = []
        for jnt in armJnt_list:
            locName = jnt.replace("_jnt", "_temp_loc")
            loc = cmds.spaceLocator(n=locName)[0]
            cmds.delete(cmds.pointConstraint(jnt, loc, mo=False))
            cmds.delete(cmds.orientConstraint(jnt, loc, mo=False))
            global_armPConstraint_list.append(cmds.pointConstraint(loc, jnt, mo=False))
            global_armLoc_list.append( loc )
            armLoc_list.append( loc )

        for i in range(0, len(armLoc_list)):
            if i < len(armLoc_list)-1:
                cmds.parent( armLoc_list[i+1], armLoc_list[i] )

def createLeg():
    nme = getTextBox_text(ikfk_switchName)
    nme = prefixName+nme
    
    cmds.select(clear=True)
    
    leg_jnt = cmds.joint( name=nme+'_l_leg_jnt', p=[0,10,0])
    knee_jnt = cmds.joint( name=nme+'_l_knee_jnt', p=[0,5,2])
    cmds.joint( leg_jnt, e=True, sao='yup', oj='xyz',zso=True )
    ankle_jnt = cmds.joint( name=nme+'_l_ankle_jnt', p=[0,1,-1])
    cmds.joint( knee_jnt, e=True, sao='yup', oj='xyz',zso=True )
    ball_jnt = cmds.joint( name=nme+'_l_ball_jnt', p=[0,0,0] )
    cmds.joint( ankle_jnt, e=True, sao='yup', oj='xyz',zso=True )
    toe_jnt = cmds.joint( name=nme+'_l_toe_jnt', p=[0,0,2] )
    cmds.joint( ball_jnt, e=True, sao='yup', oj='xyz',zso=True )
    toe_end_jnt = cmds.joint( name=nme+'_l_toe_end_jnt', p=[0,0,3] )
    cmds.joint( toe_jnt, e=True, sao='yup', oj='xyz',zso=True )
    
    legJnt_list = [ leg_jnt, knee_jnt, ankle_jnt, ball_jnt, toe_jnt, toe_end_jnt ]
    legLoc_list = []
    for jnt in legJnt_list:
        locName = jnt.replace("_jnt", "_temp_loc")
        loc = cmds.spaceLocator(n=locName)[0]
        cmds.delete(cmds.pointConstraint(jnt, loc, mo=False))
        cmds.delete(cmds.orientConstraint(jnt, loc, mo=False))
        global_armPConstraint_list.append(cmds.pointConstraint(loc, jnt, mo=False))
        global_armLoc_list.append( loc )
        legLoc_list.append( loc )

    for i in range(0, len(legLoc_list)):
        if i < len(legLoc_list)-1:
            cmds.parent( legLoc_list[i+1], legLoc_list[i] )

def createLegIK():

    cmds.select(clear=True)
    global globalCtrl
    # create ik and fk joints and controls
    if not getTextBox_text(prefixText):
        cmds.confirmDialog( title='Error', message='Error: Please specify a name for your character/creature.', 
                            button=['Ok'])
        print 'Error: Please specify a name for your character/creature.'
    else:
        print prefixName
        if not cmds.objExists( prefixName+'global_ctrl' ):
            globalCtrl = global_ctrl() # create global ctrl
        else:
            globalCtrl = prefixName+'global_ctrl'
        print globalCtrl
    
        if not getTextBox_text(jointTextBox):
            cmds.confirmDialog( title='Error', message='Error: Please use the "Get Joint" button to specify joint name, and type a name for the joints.', 
                button=['Ok'])
            print 'Error: Please use the "Get Joint" button to specify joint name, and type a name for the joints.'
        else:
            if not getTextBox_text(ikfk_switchName):
                cmds.confirmDialog( title='Error', message='Error: Please type a name for the joints.', 
                button=['Ok'])
                print 'Error: Please type a name for the joints.'
            else:
                
                legGrp_list = []
                ik_List = createIK()
                #break
                nme = getTextBox_text(ikfk_switchName)    
                nme = prefixName+nme
                 
                firstJoint = ik_List[0][0]
                jointList_children = getChildren( firstJoint, 'joint' )
                jointList = [firstJoint]
                if not jointList_children:
                    print 'No children in this list'
                else:    
                    for i in range(1,len(jointList_children)+1):
                        jointList.append(getLastItem(jointList_children, i))
                
                print jointList
                
                footJnt_list = [ jointList[2], jointList[3], jointList[4] ]
                ankleJnt = footJnt_list[0]
                ballJnt = footJnt_list[1]
                toeJnt = footJnt_list[2]
                
                # create empty groups for the foot roll setup
                cmds.select(clear=True)
                ikHndle_grp = cmds.group( n=nme+'_ikHandle_grp', em=True)
                cmds.select(clear=True)
                ankle_grp = cmds.group( n=nme+'_ankle_grp', em=True)
                ankle_grp_0 = cmds.group( ankle_grp, name=ankle_grp+'_0' )
                cmds.select(clear=True)
                ball_grp = cmds.group( n=nme+'_ball_grp', em=True)
                ball_grp_0 = cmds.group( ball_grp, name=ball_grp+'_0' )
                cmds.select(clear=True)
                toeEnd_grp = cmds.group( n=nme+'_toeEnd_grp', em=True)
                toeEnd_grp_0 = cmds.group( toeEnd_grp, name=toeEnd_grp+'_0' )
                cmds.select(clear=True)
                toe_grp = cmds.group( n=nme+'_toe_grp', em=True)
                toe_grp_0 = cmds.group( toe_grp, name=toe_grp+'_0' )
                cmds.select(clear=True)
                
                # move them to the joint positions
                #cmds.delete( cmds.pointConstraint( ankleJnt, ikHndle_grp, mo=False ) )
                #cmds.delete( cmds.pointConstraint( ankleJnt, ankle_grp, mo=False ) )
                #cmds.delete( cmds.pointConstraint( ballJnt, ball_grp, mo=False ) )
                #cmds.delete( cmds.pointConstraint( ballJnt, toe_grp, mo=False ) )
                #cmds.delete( cmds.pointConstraint( toeJnt, toeEnd_grp, mo=False ) )
               
                cmds.delete( cmds.parentConstraint( ankleJnt, ikHndle_grp, mo=False ) )
                cmds.delete( cmds.parentConstraint( ankleJnt, ankle_grp_0, mo=False ) )
                cmds.delete( cmds.parentConstraint( ballJnt, ball_grp_0, mo=False ) )
                cmds.delete( cmds.parentConstraint( ballJnt, toe_grp_0, mo=False ) )
                cmds.delete( cmds.parentConstraint( toeJnt, toeEnd_grp_0, mo=False ) )
               
                # get the names form ik function
                ikCtrl = ik_List[4]
                wristBlendLoc = ik_List[5]
                legIK = getChildren( wristBlendLoc, 'ikHandle' )[0]
                
                print ikCtrl
                print 'IK LIST ------------------------------------'
                print ik_List
                print 'FK LIST ------------------------------------'
                
                # create ikSC for foot roll setup
                ankleIk = createIkHandle( nme+'_ankleIkSc', ankleJnt, ballJnt, 'ikSCsolver' )
                toeIk = createIkHandle( nme+'_toeIkSc', ballJnt, toeJnt, 'ikSCsolver' )
                
                
                print ankleIk
                print toeIk
                
                # parent the correct groups in their hierarchy and parent ikSCs
                cmds.parent( ikHndle_grp, wristBlendLoc )
                cmds.parent( legIK, ball_grp )
                cmds.parent( toeIk[0], toe_grp )
                cmds.parent( ankleIk[0], toeEnd_grp )
                cmds.parent( ball_grp_0, toeEnd_grp )
                cmds.parent( toe_grp_0, toeEnd_grp )
                cmds.parent( toeEnd_grp_0, ankle_grp )
                cmds.parent( ankle_grp_0, ikHndle_grp )
                cmds.orientConstraint( ikCtrl, ikHndle_grp, mo=True )
                
                # create controls and add attributes to foot ctrl
                cmds.addAttr( ikCtrl, longName='footRoll', shortName='fr',attributeType="double", 
                    min=-10, max=10, defaultValue=0, keyable=True )
                cmds.addAttr( ikCtrl, longName='toeWiggleUpDown', shortName='twud',attributeType="double", 
                    min=-10, max=10, defaultValue=0, keyable=True )
                cmds.addAttr( ikCtrl, longName='toeWiggleLeftRight', shortName='twlr',attributeType="double", 
                    min=-10, max=10, defaultValue=0, keyable=True )    
                cmds.addAttr( ikCtrl, longName='footLift', shortName='fl',attributeType="double", 
                    min=-10, max=10, defaultValue=0, keyable=True )
                cmds.addAttr( ikCtrl, longName='footYaw', shortName='fy',attributeType="double", 
                    min=-10, max=10, defaultValue=0, keyable=True )  
                cmds.addAttr( ikCtrl, longName='footPitch', shortName='fp',attributeType="double", 
                    min=-10, max=10, defaultValue=0, keyable=True )        
                cmds.addAttr( ikCtrl, longName='ballLift', shortName='bl',attributeType="double", 
                    min=-10, max=10, defaultValue=0, keyable=True )    
                cmds.addAttr( ikCtrl, longName='ballYaw', shortName='bly',attributeType="double", 
                    min=-10, max=10, defaultValue=0, keyable=True )  
                cmds.addAttr( ikCtrl, longName='ballRoll', shortName='blr',attributeType="double", 
                    min=-10, max=10, defaultValue=0, keyable=True ) 
                
                #rollOrient = 'Z'# HEAD BROKEN NECK ROLL / :(
                #pitchOrient = 'X' # HEAD DOWN AND UP
                #yawOrient = 'Y' # HEAD LOOK LEFT AND RIGHT
                
                #rollOrient = 'X' # HEAD BROKEN NECK ROLL / :(
                #pitchOrient = 'Y' # HEAD DOWN AND UP
                #yawOrient = 'Z' # HEAD LOOK LEFT AND RIGHT
                
                rollOrient = getTextBox_text(g_rollOrient)
                pitchOrient = getTextBox_text(g_pitchOrient)
                yawOrient = getTextBox_text(g_yawOrient)
                
                createSDK( ikCtrl, 'toeWiggleUpDown', toe_grp, 'rotate'+pitchOrient, 0, 10, 0, -90)
                createSDK( ikCtrl, 'toeWiggleUpDown', toe_grp, 'rotate'+pitchOrient, 0, -10, 0, 100)
                createSDK( ikCtrl, 'toeWiggleLeftRight', toe_grp, 'rotate'+yawOrient, 0, 10, 0, 90)
                createSDK( ikCtrl, 'toeWiggleLeftRight', toe_grp, 'rotate'+yawOrient, 0, -10, 0, -90)

                createSDK( ikCtrl, 'footLift', toeEnd_grp, 'rotate'+pitchOrient, 0, 10, 0, 100)
                createSDK( ikCtrl, 'footLift', toeEnd_grp, 'rotate'+pitchOrient, 0, -10, 0, -100)
                createSDK( ikCtrl, 'footYaw', toeEnd_grp, 'rotate'+yawOrient, 0, 10, 0, 90)
                createSDK( ikCtrl, 'footYaw', toeEnd_grp, 'rotate'+yawOrient, 0, -10, 0, -90)
                createSDK( ikCtrl, 'footPitch', toeEnd_grp, 'rotate'+rollOrient, 0, 10, 0, 90)
                createSDK( ikCtrl, 'footPitch', toeEnd_grp, 'rotate'+rollOrient, 0, -10, 0, -90)
                
                createSDK( ikCtrl, 'ballLift', ball_grp, 'rotate'+pitchOrient, 0, 10, 0, 90)
                createSDK( ikCtrl, 'ballLift', ball_grp, 'rotate'+pitchOrient, 0, -10, 0, -90)
                createSDK( ikCtrl, 'ballYaw', ball_grp, 'rotate'+yawOrient, 0, 10, 0, 50)
                createSDK( ikCtrl, 'ballYaw', ball_grp, 'rotate'+yawOrient, 0, -10, 0, -50)
                createSDK( ikCtrl, 'ballRoll', ball_grp, 'rotate'+rollOrient, 0, 10, 0, 70)
                createSDK( ikCtrl, 'ballRoll', ball_grp, 'rotate'+rollOrient, 0, -10, 0, -70)
                
                createSDK( ikCtrl, 'footRoll', ball_grp, 'rotate'+pitchOrient, 0, 5, 0, 50)
                createSDK( ikCtrl, 'footRoll', toeEnd_grp, 'rotate'+pitchOrient, 0, 2, 0, 0)
                createSDK( ikCtrl, 'footRoll', toeEnd_grp, 'rotate'+pitchOrient, 0, 5, 0, 30)
                createSDK( ikCtrl, 'footRoll', toeEnd_grp, 'rotate'+pitchOrient, 0, 10, 0, 90)
                createSDK( ikCtrl, 'footRoll', ball_grp, 'rotate'+pitchOrient, 0, 10, 0, 0)
                createSDK( ikCtrl, 'footRoll', ball_grp, 'rotate'+pitchOrient, 0, -5, 0, -50)
                createSDK( ikCtrl, 'footRoll', toeEnd_grp, 'rotate'+pitchOrient, 0, -2, 0, 0)
                createSDK( ikCtrl, 'footRoll', toeEnd_grp, 'rotate'+pitchOrient, 0, -5, 0, -30)
                createSDK( ikCtrl, 'footRoll', toeEnd_grp, 'rotate'+pitchOrient, 0, -10, 0, -90)
                createSDK( ikCtrl, 'footRoll', ball_grp, 'rotate'+pitchOrient, 0, -10, 0, 0)
                #createSDK( ikCtrl, 'footRoll', toe_grp, 'rotate'+pitchOrient, 0, -10, 0, -50)
                #createSDK( ikCtrl, 'footRoll', ball_grp, 'rotate'+pitchOrient, 0, -10, 0, -30)
                #createSDK( ikCtrl, 'footRoll', ankle_grp, 'rotate'+pitchOrient, 0, -10, 0, -30)
                

                legGrp_list.append( ik_List[1] )
                
                mainJoint = getTextBox_text(jointTextBox)
                cmds.delete(mainJoint)
                
                cmds.select(ik_List[0][0])
                ikLegJointsGrp = cmds.group ( name=nme+'_joints_grp')
                cmds.select(clear=True)
                legGrp_list.append( ikLegJointsGrp )
                
                legGrpNme = nme+'_grp'
                cmds.select(clear=True)
                for item in legGrp_list:
                    cmds.select( item, add=True )
                legGrp = cmds.group( name=legGrpNme )
                cmds.select(clear=True)
                
                cmds.parent( legGrp, globalCtrl )
            
                setRootNaming()
    

def createShoulderIK():
    global globalCtrl 
    if not cmds.objExists( prefixName+'global_ctrl' ):
        globalCtrl = global_ctrl() # create global ctrl
    else:
        globalCtrl = prefixName+'global_ctrl'
    
    print globalCtrl
    
    setTempNaming()
    
    shoulderGrp_list = []
    
    cmds.select(clear=True)
    print '*** start of createShoulderIK function ***-------------------------'
    shoulderJnt = getTextBox_text(jointTextBox)
    shoulderEndJnt = getChildren( shoulderJnt, 'joint' )
    print 'shoulderEndJnt = '+str(shoulderEndJnt)
    print 'shoulderEndJnt[0] = '+shoulderEndJnt[0]
    #cmds.joint( shoulderJnt, e=True, sao='zup', oj='xyz', zso=True, children=True )
    
    cmds.parent( shoulderEndJnt[0], world=True )
    cmds.delete(cmds.orientConstraint(shoulderJnt, shoulderEndJnt[0], mo=False))
    cmds.parent( shoulderEndJnt[0], shoulderJnt )
    shoulderGrp_list.append( shoulderJnt )
    
    ikHndle = createIkHandle( shoulderEndJnt[0], shoulderJnt, shoulderEndJnt[0], 'ikSCsolver' )
    
    #ikHndle = cmds.ikHandle( n=shoulderEndJnt[0]+'_ik_Handle', 
    #                        sj=shoulderJnt, ee=shoulderEndJnt[0],  sol='ikSCsolver') 
    #shoulderGrp_list.append( ikHndle[0] )
    #cmds.select(ikHndle[0])   
    #ikEffector = cmds.ikHandle( ee=True, query=True )
    #cmds.rename( ikEffector, shoulderEndJnt[0]+'_ik_effector' )       
    #cmds.setAttr( ikHndle[0]+'.visibility', 0 )          
    #cmds.select(clear=True)
    shoulderGrp_list.append( ikHndle[0] )
    
    shoulderLocName = shoulderJnt.replace("_jnt", '_loc')
    print 'shoulderLocName = '+shoulderLocName
    shoulderLoc = cmds.spaceLocator(n=shoulderLocName)[0]
    print 'shoulderLoc = '+shoulderLoc
    cmds.pointConstraint(shoulderJnt, shoulderLoc, mo=False)
    cmds.delete(cmds.orientConstraint(shoulderJnt, shoulderLoc, mo=False))
    shoulderGrp_list.append(shoulderLoc)
    cmds.setAttr( shoulderLoc+'.visibility', 0 )  
    
    shoulderEndLocName = shoulderEndJnt[0].replace("_jnt", '_loc')
    print 'shoulderEndLocName = '+shoulderEndLocName
    shoulderEndLoc = cmds.spaceLocator(n=shoulderEndLocName)[0]
    print 'shoulderEndLoc = '+shoulderEndLoc
    cmds.delete(cmds.pointConstraint(shoulderEndJnt[0], shoulderEndLoc, mo=False))
    cmds.delete(cmds.orientConstraint(shoulderEndJnt[0], shoulderEndLoc, mo=False))
    cmds.setAttr( shoulderEndLoc+'.visibility', 0 )  
    
    shoulderLocPos = cmds.getAttr( shoulderLoc+'.translate' )
    # weird bug in maya that if two locs are on the same position even though they are different
    # and you specify unique names it seems as though they will become a distance measure
    # or one will override the other one. So to avoid this I move the locator somewhere else
    # and then move it back
    cmds.xform( shoulderEndLoc, translation = (10,10,10), os=True, r=True )
    shoulderEndLocPos = cmds.getAttr( shoulderEndLoc+'.translate' )
    print 'shoulderLocPos = '+str(shoulderLocPos)
    print 'shoulderEndLocPos = '+str(shoulderEndLocPos)
    print 'shoulderLocPos[0] = '+str(shoulderLocPos[0])
    print 'shoulderEndLocPos[0] = '+str(shoulderEndLocPos[0])
    shoulderDistDim = cmds.distanceDimension( startPoint=( shoulderLocPos[0] ), endPoint=( shoulderEndLocPos[0] ))
    print 'distDim1 = '+shoulderDistDim
    shoulderDistDim = cmds.rename( shoulderDistDim, shoulderLoc+'_distanceDimensionShape' )
    print 'distDim1 = '+shoulderDistDim
    cmds.select( shoulderDistDim )
    distShoulderDim = cmds.pickWalk( direction='up' )
    distShoulder = cmds.rename( distShoulderDim, shoulderLoc+'_distanceDimension' )
    print 'distShoulder = '+distShoulder
    cmds.setAttr( distShoulder+'.visibility', 0 )
    cmds.xform( shoulderEndLoc, translation = (-10,-10,-10), os=True, r=True )
    shoulderGrp_list.append(distShoulder)
    
    shoulderCtrl = ikCtrl()
    shoulderCtrlName = shoulderJnt.replace("_jnt", "_ctrl")
    shoulderCtrl = cmds.rename( shoulderCtrl, shoulderCtrlName )
    shoulderCtrlGrp = cmds.group( shoulderCtrl, n=shoulderCtrl+'_0' ) 
    cmds.group( shoulderCtrl, n=shoulderCtrl+'_sdk' ) 
    cmds.delete(cmds.pointConstraint(shoulderEndJnt[0], shoulderCtrlGrp, mo=False))
    cmds.delete(cmds.orientConstraint(shoulderEndJnt[0], shoulderCtrlGrp, mo=False))
    cmds.parent( shoulderEndLoc, shoulderCtrl )
    cmds.pointConstraint( shoulderCtrl, ikHndle[0] )
    shoulderGrp_list.append(shoulderCtrlGrp)
    
    shoulderEndJnt_translateX = cmds.getAttr( shoulderEndJnt[0]+'.translateX' )
    cmds.setDrivenKeyframe( shoulderEndJnt[0]+'.translateX', value=shoulderEndJnt_translateX, cd=distShoulder+'.distance', dv=shoulderEndJnt_translateX)
    cmds.setDrivenKeyframe( shoulderEndJnt[0]+'.translateX', value=shoulderEndJnt_translateX*2, cd=distShoulder+'.distance', dv=shoulderEndJnt_translateX*2) # set SDK
    cmds.selectKey( shoulderEndJnt[0], attribute='translateX', add=True, k=True, f=(shoulderEndJnt_translateX,shoulderEndJnt_translateX*2))
    cmds.setInfinity( poi='cycleRelative', pri='cycleRelative' )

    cmds.select( shoulderEndJnt[0] )
    shoulderSDK_translateX_curve = cmds.keyframe( query=True, lastSelected=True, name=True )
    cmds.select(clear=True)
    print shoulderSDK_translateX_curve
    global_shoulder_MD = globalFixNode( prefixName+'global_shoulderFix_MD', distShoulder, 'distance' )
    cmds.connectAttr( global_shoulder_MD+'.outputX', shoulderSDK_translateX_curve[0]+'.input', f=True )

    print 'Shoulder Joint = '+shoulderJnt
    print 'Shoulder Loc = '+shoulderLoc
    #print 'Shoulder Loc [0] = '+shoulderLoc[0]
    #print 'Shoulder End Joint = '+shoulderEndJnt
    print 'Shoulder End Joint [0] = '+shoulderEndJnt[0]
    print 'Shoulder End Loc = '+shoulderEndLoc
    #print 'Shoulder End Loc[0] = '+shoulderEndLoc[0]
    
    nme = getTextBox_text(ikfk_switchName)
    
    shoulderGrpNme = prefixName+nme+'_shoulder_grp'
    cmds.select(clear=True)
    for item in shoulderGrp_list:
        cmds.select( item, add=True )
    shoulderGrp = cmds.group( name=shoulderGrpNme )
    cmds.select(clear=True)
    
    cmds.parent( shoulderGrp, globalCtrl )
    
    setRootNaming()
    print '*** end of createShoulderIK function ***-------------------------'
    
    
def getFKControls():
    
    firstJoint = getTextBox_text(jointTextBox)
    jointList_children = getChildren( firstJoint, 'joint' )
    jointList = [firstJoint]
    if not jointList_children:
        print 'No children in this list'
    else:    
        for i in range(1,len(jointList_children)):
            jointList.append(getLastItem(jointList_children, i))

    name = getTextBox_text(ikfk_switchName)
    jointIndex = 0
    newJointList = []
    for jnt in jointList: # iterate through joint chain and rename to ik/fk
        cmds.select(jnt)
        newJointList.append(cmds.rename(name+'_'+str(jointIndex)+'_jnt'))
        jointIndex = jointIndex + 1
                
    createSimpleFK( newJointList, '' )

def oneSimpleFK():
    firstJoint = getTextBox_text(jointTextBox)
    ctrlName = firstJoint.replace("_jnt", "_ctrl")
    ctrl = cmds.circle( nr=(1, 0, 0), r=1,  n=ctrlName)[0]
    group = cmds.group(ctrl, n=ctrl + "_sdk")
    offset = cmds.group(group, n=ctrl + "_offset")
    cmds.delete(cmds.parentConstraint(firstJoint, offset, mo=False))
    #cmds.orientConstraint(ctrl, firstJoint, mo=False)

def createSimpleFK( _fkList, _nme ):
    ctrl_list = []
    i = 0
    fkGrpName = ''
    for jnt in _fkList:
        if i == 0:
            ctrlName = jnt.replace("_jnt", '_'+_nme+"_ctrl")
            ctrl = cmds.circle( nr=(1, 0, 0), r=1,  n=ctrlName)[0]
            ctrl_list.append(ctrl)
            group = cmds.group(ctrl, n=ctrl + "_sdk")
            offset = cmds.group(group, n=ctrl + "_offset")
            fkGrpName = offset
            ctrl_list.append(offset)
            cmds.delete(cmds.parentConstraint(jnt, offset, mo=False))
            cmds.orientConstraint(ctrl, jnt, mo=False)
            i = i+1
        else:
            ctrlName = jnt.replace("_jnt", '_'+_nme+"_ctrl")
            ctrl = cmds.circle( nr=(1, 0, 0), r=1,  n=ctrlName)[0]
            ctrl_list.append(ctrl)
            group = cmds.group(ctrl, n=ctrl + "_sdk")
            offset = cmds.group(group, n=ctrl + "_offset")
            ctrl_list.append(offset)
            cmds.delete(cmds.parentConstraint(jnt, offset, mo=False))
            cmds.orientConstraint(ctrl, jnt, mo=False)
        
    for i in range(0, len(ctrl_list), 2):
        if i+3 > len(ctrl_list):
            #print 'out of range'
            break
        else:
            cmds.parent( ctrl_list[i+3],
                         ctrl_list[i] )
            #print ctrl_list[i+3]
            #print 'parent this thing to'
            #print ctrl_list[i]
    return fkGrpName


def createFK():
    jntList = createTempJointChain()
    #cmds.joint( jntList[0], e=True, sao='zup', oj='xyz', zso=True, children=True )
    cmds.delete(jntList[-1])
    jntList.pop()
    #cmds.joint( jntList[0], e=True, sao='zup', oj='xyz', zso=True, children=True )
    
    nme = getTextBox_text(ikfk_switchName)
    fkGrpName = createSimpleFK( jntList, nme )
            
    fkJointList = renameJoints(jntList, 'fk')
    
    return fkJointList, fkGrpName

def createIK():
    # create joints for ik
    jntList = createTempJointChain()
    # delete last in chain which is end joint we do not need
    lastJnt = jntList[-1]
    jntList.pop()
    # orient them
    print jntList
    
    
    #cmds.joint( jntList[0], e=True, sao='zup', oj='xyz', zso=True, children=True )
    
    armGrp_list = []
    
    # assign appropriate names
    startJnt = jntList[0]
    midJnt = jntList[1] 
    endJnt = jntList[2] 

    # create locators for measurement for ik stretchy
    distanceLoc = createDistanceLocs( jntList )
    
    distanceDims = getDistanceDimensions( distanceLoc )
    for dist in distanceDims:
        armGrp_list.append(dist)
    
    armLoc = distanceLoc[0]
    elbowLoc = distanceLoc[1]
    handLoc = distanceLoc[2]
    upperDist = distanceDims[0]
    lowerDist = distanceDims[1]
    ctrlDist = distanceDims[2]
    armGrp_list.append( armLoc )
    
    ikHndle = createIkHandle( prefixName+endJnt, startJnt, endJnt, 'ikRPsolver')
    
    # create ik handle
    #ikHndle = cmds.ikHandle( n=prefixName+endJnt+'_ik_Handle', sj=startJnt, ee=endJnt,  sol='ikRPsolver') 
    #cmds.select(ikHndle[0])   
    #ikEffector = cmds.ikHandle( ee=True, query=True )
    #cmds.rename( ikEffector, prefixName+endJnt+'_ik_effector' )       
    #cmds.setAttr( ikHndle[0]+'.visibility', 0 )
    
    # create pole vector locator and hierarchy
    poleVector_ctrl = ikPVCtrl2()
    #pv = pv[0]
    pvGrp = cmds.group( poleVector_ctrl, n=poleVector_ctrl+'_0' ) 
    armGrp_list.append(pvGrp)
    cmds.group( poleVector_ctrl, n=poleVector_ctrl+'_sdk' ) 
    # orient and aim the pole vector correctly
    cmds.delete(cmds.pointConstraint( startJnt, endJnt, pvGrp, mo=False ) )
    cmds.delete(cmds.aimConstraint( midJnt, pvGrp, mo=False ) )
    # need to move pivot of pv ctrl offset to elbow later so that can rotate 
    elbowTargetPos = cmds.xform( elbowLoc, translation = True, query=True, ws=True )
    poleVectorPos = cmds.xform( pvGrp, translation = True, query=True, ws=True )
    
    pvDistance = lengthVector( elbowTargetPos[0], elbowTargetPos[1], elbowTargetPos[2],
                                 poleVectorPos[0], poleVectorPos[1], poleVectorPos[2]  )
    
    cmds.xform( pvGrp, translation = [pvDistance, 0, 0], os=True, r=True  )
    
    #cmds.parentConstraint( poleVector_ctrl, elbowLoc, mo=True )
    cmds.parent( elbowLoc, poleVector_ctrl )
    cmds.poleVectorConstraint( poleVector_ctrl, ikHndle[0] ) # create pv

    # create ik control
    ikControl = ikCtrl()
    ikGrp = cmds.group( ikControl, n=ikControl+'_0' ) 
    armGrp_list.append(ikGrp)
    cmds.group( ikControl, n=ikControl+'_sdk' ) 
    cmds.delete(cmds.pointConstraint(endJnt, ikGrp, mo=False))
    cmds.delete(cmds.orientConstraint(endJnt, ikGrp, mo=False))
    cmds.orientConstraint( ikControl, endJnt, mo=False )
    cmds.parent( handLoc, ikControl ) # parent distance loc to ik control
    cmds.aimConstraint(ikControl, armLoc, mo=True)
    
    nme = getTextBox_text(ikfk_switchName)
    
    # create wrist blend locator
    totalDist = cmds.getAttr( ctrlDist+'.distance' )
    wristBlendLoc = cmds.spaceLocator(n=prefixName+nme+'_wristBlend_loc')[0]
    cmds.delete(cmds.pointConstraint(endJnt, wristBlendLoc, mo=False) )
    cmds.delete(cmds.orientConstraint(endJnt, wristBlendLoc, mo=False) )
    armGrp_list.append( wristBlendLoc )
    cmds.setAttr( wristBlendLoc+'.visibility', 0 )
    
    # create wrist soft locator 
    wristSoftLoc = cmds.spaceLocator(n=prefixName+nme+'_wristSoft_loc')[0]
    wristSoftLoc_grp = cmds.group( wristSoftLoc, n=wristSoftLoc+'_0' ) 
    wristSoftLoc_sdk = cmds.group( wristSoftLoc, n=wristSoftLoc+'_sdk' ) 
    cmds.delete(cmds.pointConstraint(startJnt, wristSoftLoc_grp, mo=False))
    cmds.delete(cmds.aimConstraint(endJnt, wristSoftLoc_grp, mo=False))
    cmds.xform( wristSoftLoc, translation = (totalDist, 0, 0), r=True )
    cmds.setAttr( wristSoftLoc+'.visibility', 0 )
    
    # create distance dimensions
    # move locs out of way to create new distance dimensions (maya bug)
    cmds.xform( wristBlendLoc, translation = (10,10,10), os=True, r=True )
    cmds.xform( wristSoftLoc, translation = (10,10,10), os=True, r=True )
    
    # get locators position
    armLocPos = cmds.getAttr( armLoc+'.translate' )
    wristBlendPos = cmds.getAttr( wristBlendLoc+'.translate' )
    wristSoftLocPos = cmds.xform( wristSoftLoc, translation=True, query=True, ws=True )
    
    # create distances dimensions
    distDim1 = cmds.distanceDimension( startPoint=( armLocPos[0] ), endPoint=( wristBlendPos[0] ))
    
    distDim2 = cmds.distanceDimension( startPoint=( wristSoftLocPos ), endPoint=( wristBlendPos[0] ))
    
    distDim1 = cmds.rename( distDim1, wristBlendLoc+'_distanceDimensionShape' )
    cmds.select( distDim1 )
    distWristBlendLocDim = cmds.pickWalk( direction='up' )
    distWristBlendLoc = cmds.rename( distWristBlendLocDim, wristBlendLoc+'_distanceDimension' )
    
    distDim2 = cmds.rename( distDim2, wristSoftLoc+'_distanceDimensionShape' )
    cmds.select( distDim2 )
    distWristSoftLocDim = cmds.pickWalk( direction='up' )
    distWristSoftLoc = cmds.rename( distWristSoftLocDim, wristSoftLoc+'_distanceDimension' )
    
    cmds.xform( wristBlendLoc, translation = (-10,-10,-10), os=True, r=True )
    cmds.xform( wristSoftLoc, translation = (-10,-10,-10), os=True, r=True )
    
    cmds.setAttr( distWristSoftLoc+'.visibility', 0 )
    cmds.setAttr( distWristBlendLoc+'.visibility', 0 )
    
    cmds.select(clear=True)

    #cmds.parentConstraint( wristBlendLoc, ikHndle[0], mo=True )
    cmds.parentConstraint(armLoc, wristSoftLoc_sdk, mo=True)
    wristPC = cmds.pointConstraint(wristSoftLoc, wristBlendLoc, mo=True, w=0 )
    stretchPC = cmds.pointConstraint(handLoc, wristBlendLoc, mo=True, w=1)
    cmds.parent( ikHndle[0], wristBlendLoc )

    armGrp_list.append( wristBlendLoc )
    armGrp_list.append( distWristBlendLoc )
    armGrp_list.append( wristSoftLoc_grp )
    armGrp_list.append( distWristSoftLoc )
    # move back the locators to original location
    
    wristStretchDist = ( distWristBlendLoc, distWristSoftLoc )
    

    # create stretchy joints
    blendAttrNodes_and_checkStretchCond = addStretchyIKJoints( jntList, distanceDims, ikControl, wristStretchDist )

    # create sdk for elbow pin
    upperBlendNode = blendAttrNodes_and_checkStretchCond[0]
    lowerBlendNode = blendAttrNodes_and_checkStretchCond[1]
    checkStretch_condition = blendAttrNodes_and_checkStretchCond[2]
    cmds.connectAttr( checkStretch_condition+'.outColorR', wristSoftLoc+'.translateX', f=True )
    elbowSnapName = 'elbowSnap'
    cmds.addAttr( poleVector_ctrl, longName=elbowSnapName, shortName='es',attributeType="double", 
                    min=0, max=10, defaultValue=0, keyable=True )
    
    # driver name, driver attribute, driven name, driven attribute
    # driver first and second values, driven first and second values
    createSDK( poleVector_ctrl, elbowSnapName, upperBlendNode, 'attributesBlender', 
            0, 10, 0, 1 )
    createSDK( poleVector_ctrl, elbowSnapName, lowerBlendNode, 'attributesBlender', 
            0, 10, 0, 1 )

    wristSoftLoc_nameFix = wristSoftLoc[5:]
    handLoc_nameFix = handLoc[10:]
    createSDK( ikControl, 'ikStretch', wristPC[0], wristSoftLoc_nameFix+'W0', 0, 1, 1, 0 ) # no stretch
    createSDK( ikControl, 'ikStretch', stretchPC[0], handLoc_nameFix+'W1', 1, 0, 1, 0 ) # to stretch 
    
    cmds.delete(lastJnt)
    ikJointList = renameJoints(jntList, 'ik')
    
    armGrpNme = prefixName+nme+'_ik_grp'
    cmds.select(clear=True)
    for item in armGrp_list:
        cmds.select( item, add=True )
    ikArmGrp = cmds.group( name=armGrpNme )
    cmds.select(clear=True)
    
    
    return ikJointList, ikArmGrp, ikGrp, pvGrp, ikControl, wristBlendLoc

def createIKFK():
    cmds.select(clear=True)
    global globalCtrl
    # create ik and fk joints and controls
    if not getTextBox_text(prefixText):
        cmds.confirmDialog( title='Error', message='Error: Please specify a name for your character/creature.', 
                            button=['Ok'])
        print 'Error: Please specify a name for your character/creature.'
    else:
        print prefixName
        if not cmds.objExists( prefixName+'global_ctrl' ):
            globalCtrl = global_ctrl() # create global ctrl
        else:
            globalCtrl = prefixName+'global_ctrl'
        print globalCtrl
    
        if not getTextBox_text(jointTextBox):
            cmds.confirmDialog( title='Error', message='Error: Please use the "Get Joint" button to specify joint name, and type a name for the joints.', 
                button=['Ok'])
            print 'Error: Please use the "Get Joint" button to specify joint name, and type a name for the joints.'
        else:
            if not getTextBox_text(ikfk_switchName):
                cmds.confirmDialog( title='Error', message='Error: Please type a name for the joints.', 
                button=['Ok'])
                print 'Error: Please type a name for the joints.'
            else:
                leftArmGrp_list = []
                ik_List = createIK()
                fk_List = createFK()
                print 'IK LIST ------------------------------------'
                print ik_List
                print 'FK LIST ------------------------------------'
                print fk_List
                
                cmds.setAttr( ik_List[0][0]+'.visibility', 0 )
                cmds.setAttr( fk_List[0][0]+'.visibility', 0 )
                
                leftArmGrp_list.append( ik_List[1] )
                leftArmGrp_list.append( fk_List[1] )
                global_joints_groupList.append( ik_List[0][0] )
                global_joints_groupList.append( fk_List[0][0] )
                
                # get first joint and its children and put it in a list
                # this is the main bind joint
                mainJoint = getTextBox_text(jointTextBox)
                global_joints_groupList.append( mainJoint )
                mainJoint_children = getChildren( mainJoint, 'joint' )
                mainList = [mainJoint, getLastItem(mainJoint_children, 1), getLastItem(mainJoint_children, 2)]
                
                ikfkCtrl = IKFK_ctrl() # create ikfk control switch
                leftArmGrp_list.append( ikfkCtrl )
                cmds.parentConstraint(mainList[2], ikfkCtrl, mo=False)
                lockHide_attributes( ikfkCtrl, True, True, False )
                # add attribute to ikfk control
                switchNme = getTextBox_text(ikfk_switchName)
                switchAttrNme = prefixName+switchNme+'IKFKSwitch'
                cmds.addAttr( ikfkCtrl, longName=switchAttrNme, shortName=switchNme,attributeType="double", 
                                min=0, max=10, defaultValue=0, keyable=True )
                                
                createSDK( ikfkCtrl, switchAttrNme, ik_List[2], 'visibility', 10, 0, 0, 1 )
                createSDK( ikfkCtrl, switchAttrNme, ik_List[3], 'visibility', 10, 0, 0, 1 )
                createSDK( ikfkCtrl, switchAttrNme, fk_List[1], 'visibility', 0, 10, 0, 1 )

                # here is the actual blending between fk and ik using bldColors nodes               
                jointBlendColours( switchNme, 'rotate', ik_List[0], fk_List[0], mainList, ikfkCtrl, switchAttrNme)
                jointBlendColours( switchNme, 'translate', ik_List[0], fk_List[0], mainList, ikfkCtrl, switchAttrNme )
                    
                jointsGrpNme = prefixName+switchNme+'_joints_grp'
                cmds.select(clear=True)
                for item in global_joints_groupList:
                    cmds.select( item, add=True )
                jointsGrp = cmds.group( name=jointsGrpNme )
                cmds.select(clear=True)
                leftArmGrp_list.append( jointsGrp )
                global_joints_groupList[:] = []
                
                leftArmGrpNme = prefixName+switchNme+'_grp'
                cmds.select(clear=True)
                for item in leftArmGrp_list:
                    cmds.select( item, add=True )
                leftArmGrp = cmds.group( name=leftArmGrpNme )
                cmds.select(clear=True)
                
                cmds.parent( leftArmGrp, globalCtrl )
            
                setRootNaming()

def addSplineIkStretchy( nme, _curve ):
    print _curve
    cmds.select( _curve )
    curveShape = cmds.pickWalk( direction='down' )
    curveInfoNode = cmds.arclen( curveShape[0], ch=True )
    curveInfo = cmds.rename( curveInfoNode, nme+'_spineIk_curveInfo' )
    globalCurve = cmds.duplicate( _curve )
    globalCurve = cmds.rename( globalCurve, nme+'global_spineIk_curve' )
    cmds.select( globalCurve )
    globalCurveShape = cmds.pickWalk( direction='down' )
    globalCurveInfoNode = cmds.arclen( globalCurveShape[0], ch=True )
    globalCurveInfo = cmds.rename( globalCurveInfoNode, nme+'global_spineIk_curveInfo' )
    

    distanceToStretch_PM = plusMinusNode( nme+'distanceToStretch', 'subtract',
                             curveInfo, 'arcLength', globalCurveInfo,'arcLength' )
                 
    correctAdd_Minus_MD = multiDivideNode( nme+'correctAdd_Minus', 'multiply', 
                        '', -1, distanceToStretch_PM, 'output1D' )
    
    toggleStretch_ctrl_MD = multiDivideNode( nme+'toggleStretch_ctrl', 'multiply', 
                        '', 0, correctAdd_Minus_MD, 'outputX' )
                        
    distanceStretchCurve_PM = plusMinusNode( nme+'distanceStretchCurve', 'sum',
                             curveInfo, 'arcLength', toggleStretch_ctrl_MD,'outputX' )
                                                 
    globalCurveStretchyFix_MD = multiDivideNode( nme+'globalCurveStretchyFix', 'divide',
                             distanceStretchCurve_PM , 'output1D', globalCurveInfo , 'arcLength')
    
    return globalCurveStretchyFix_MD, toggleStretch_ctrl_MD, globalCurve
    
def createSplineIKFK():
    print 'start of createSplineIKFK Function'
    global globalCtrl
    if not cmds.objExists( prefixName+'global_ctrl' ):
        globalCtrl = global_ctrl() # create global ctrl
    else:
        globalCtrl = prefixName+'global_ctrl'
    print globalCtrl
    
    nme = prefixName + 'spine_'
    
    firstJoint = getTextBox_text(jointTextBox)
    jointList_children = getChildren( firstJoint, 'joint' )
    jointList = [firstJoint]
    if not jointList_children:
        print 'No children in this list'
    else:    
        for i in range(1,len(jointList_children)):
            jointList.append(getLastItem(jointList_children, i))

    print jointList
    
    jointIndex = 0
    newJointList = []
    for jnt in jointList: # iterate through joint chain and rename to ik/fk
        cmds.select(jnt)
        newJointList.append(cmds.rename(nme+str(jointIndex)+'_jnt'))
        jointIndex = jointIndex + 1
    
    cmds.select(clear=True)
    bot_bindJoint = cmds.joint( name=nme+'_botCtrl_joint' )
    cmds.select(clear=True)
    mid_bindJoint = cmds.joint( name=nme+'_midCtrl_joint' )
    cmds.select(clear=True)
    top_bindJoint = cmds.joint( name=nme+'_topCtrl_joint' )
    cmds.select(clear=True)
    cmds.setAttr( bot_bindJoint+'.visibility', 0 ) 
    cmds.setAttr( mid_bindJoint+'.visibility', 0 ) 
    cmds.setAttr( top_bindJoint+'.visibility', 0 ) 
    
    startJnt = newJointList[0]
    endJnt = newJointList[len(newJointList)-1]
    midJnt = newJointList[len(newJointList)/2]
    
    cmds.select(clear=True)
    cmds.joint( startJnt, e=True, sao='xup', oj='yxz', zso=True, children=True )
    cmds.select(clear=True)
    
    print newJointList
    print len(newJointList)
    print len(newJointList)/2
    cmds.delete( cmds.parentConstraint( endJnt, top_bindJoint, mo=False ) )
    cmds.delete( cmds.parentConstraint( midJnt, mid_bindJoint, mo=False ) )
    cmds.delete( cmds.parentConstraint( startJnt, bot_bindJoint, mo=False ) )

    botCtrl = cmds.circle( name=nme+'spine_bot_ctrl' )[0]
    botGrp = cmds.group( botCtrl, n=botCtrl+'_0' ) 
    cmds.group( botCtrl, n=botCtrl+'_sdk' ) 
    cmds.delete( cmds.parentConstraint( startJnt, botGrp, mo=False ) )
    cmds.select(botGrp)
    cmds.rotate( 90,0,0, r=True, os=True)
    cmds.select(clear=True)
    cmds.parentConstraint( botCtrl, bot_bindJoint, mo=True )
    
    midCtrl = cmds.circle( name=nme+'spine_mid_ctrl' )[0]
    midGrp = cmds.group( midCtrl, n=midCtrl+'_0' ) 
    cmds.group( midCtrl, n=midCtrl+'_sdk' ) 
    cmds.delete( cmds.parentConstraint( midJnt, midGrp, mo=False ) )
    cmds.select(midGrp)
    cmds.rotate( 90,0,0, r=True, os=True)
    cmds.select(clear=True)
    cmds.parentConstraint( midCtrl, mid_bindJoint, mo=True )
    
    topCtrl = cmds.circle( name=nme+'spine_top_ctrl' )[0]
    topGrp = cmds.group( topCtrl, n=topCtrl+'_0' ) 
    cmds.group( topCtrl, n=topCtrl+'_sdk' ) 
    cmds.delete( cmds.parentConstraint( endJnt, topGrp, mo=False ) )
    cmds.select(topGrp)
    cmds.rotate( 90,0,0, r=True, os=True)
    cmds.select(clear=True)
    cmds.parentConstraint( topCtrl, top_bindJoint, mo=True )
    
    #spineIk = createIkHandle( nme+'spineIK', startJnt, endJnt, 'ikSplineSolver' )
    
    ikHndle = cmds.ikHandle( n=nme+'spineIK'+'_ik_Handle', 
                            sj=startJnt, ee=endJnt,  sol='ikSplineSolver', ns=3) 
    cmds.select(ikHndle[0])   
    ikEffector = cmds.ikHandle( ee=True, query=True )
    cmds.rename( ikEffector, nme+'spineIK'+'_ik_effector' )       
    cmds.select(clear=True)
    
    spineIk = ikHndle
    
    print spineIk
    
    # rename curve
    spineIk_curve = cmds.rename( spineIk[2], nme+'spineIk_curve' )
    cmds.select(spineIk_curve)
    spineIkCurveGrp = cmds.group( name=nme+'spineIk_curve_grp' )
    cmds.select(cl=True)
    cmds.setAttr( spineIkCurveGrp+'.inheritsTransform', 0 )
    
    
    print spineIk_curve
    
    getAxis = getTextBox_text(ikfk_switchName)
    print getAxis
    createIkSplineTwist(botCtrl, topCtrl, topCtrl, spineIk[0], getAxis)
    
    
    stretchyNodes = addSplineIkStretchy( nme, spineIk_curve )
    
    globalScaleCurve_MD = stretchyNodes[0]
    toggleStretch_MD = stretchyNodes[1]
    globalCurve = stretchyNodes[2]
    
    cmds.addAttr( topCtrl, longName='toggleStretch', shortName='ts',attributeType="double", 
                                min=0, max=1, defaultValue=1, keyable=True )
    
    cmds.connectAttr( topCtrl+'.toggleStretch', toggleStretch_MD+'.input1X', f=True )
    
    newJointList.pop()
    for jnt in newJointList:
        cmds.connectAttr( globalScaleCurve_MD+'.outputX', jnt+'.scaleY', f=True )
    
    cmds.skinCluster( top_bindJoint, mid_bindJoint, bot_bindJoint, spineIk_curve, tsb=True)
    
    doNotTouch_list = ( spineIk[0], spineIkCurveGrp, globalCurve)
    cmds.select(clear=True)
    for item in doNotTouch_list:
        cmds.select( item, add=True )
    doNotTouchGrp = cmds.group( name=nme+'do_not_touch_grp' )
    cmds.select(clear=True)
    cmds.setAttr( doNotTouchGrp+'.visibility', 0 ) 
    
    controls_list = ( topGrp, midGrp, botGrp, bot_bindJoint, mid_bindJoint, top_bindJoint )
    cmds.select(clear=True)
    for item in controls_list:
        cmds.select( item, add=True )
    controlsGrp = cmds.group( name=nme+'controls_grp' )
    cmds.select(clear=True)
    
    cmds.select( startJnt )
    jointsGrp = cmds.group( name=nme+'joints_grp' )
    cmds.select(clear=True)
    
    spineGrp_list = ( doNotTouchGrp , controlsGrp, jointsGrp )
    cmds.select(clear=True)
    for item in spineGrp_list:
        cmds.select( item, add=True )
    spineGrp = cmds.group( name=nme+'grp' )
    cmds.select(clear=True)
    
    cmds.parent( spineGrp ,globalCtrl)
    
    print 'splinefk'
    

##############################################################################################################
##############################################################################################################

def chooseJointCreation(jointType): 
    global jointFunction
    if ( jointType == 'Shoulder'  ): 
        jointFunction = 'createShoulderJoints'
    if ( jointType == 'Arm' ): 
        jointFunction = 'createArmJoints'
    if ( jointType == 'Leg' ): 
        jointFunction = 'createLeg'

def createJointType():
    global jointFunction
    if ( jointFunction == 'createShoulderJoints' ): 
        createShoulderJoints()
    if ( jointFunction == 'createArmJoints' ): 
        createArmJoints()
    if ( jointFunction == 'createLeg' ): 
        createLeg()
        
def chooseRigSystem(rigSystemType):
    global rigSystemFunction
    if ( rigSystemType == 'Arm IK / FK System'  ): 
        rigSystemFunction = 'createArmIKFK'
    if ( rigSystemType == 'Leg IK System'  ): 
        rigSystemFunction = 'createLegIK'      
    if ( rigSystemType == 'Shoulder IK' ): 
        rigSystemFunction = 'createShoulderIK'
    if ( rigSystemType == 'Simple FK' ): 
        rigSystemFunction = 'getFKControls'
    if ( rigSystemType == 'One Simple FK' ): 
        rigSystemFunction = 'getOneSimpleFK'
    if ( rigSystemType == 'Spline IK FK' ): 
        rigSystemFunction = 'createSplineIKFK' 

def chooseOrientation():
    print 'yo'
    orientationWindow = cmds.window(title="Choose Orientation", resizeToFitChildren=1)
    cmds.rowColumnLayout( numberOfRows=2, rowHeight=[(1, 30), (2, 60)] )
    global g_rollOrient, g_pitchOrient, g_yawOrient
    cmds.text( label='Roll Orientation ( HEAD BROKEN NECK ROLL )' )
    g_rollOrient = cmds.textField( )
    cmds.text( label = 'Pitch Orientation ( HEAD DOWN AND UP )')
    g_pitchOrient = cmds.textField( )
    cmds.text( label = 'Yaw Orientation ( HEAD LOOK LEFT AND RIGHT )' )
    g_yawOrient = cmds.textField( )
    cmds.button( label='Create Leg IK', command='createLegIK()', bgc=[0,1,1] )
    cmds.showWindow(orientationWindow)

def createRigSystem():
    global rigSystemFunction
    if ( rigSystemFunction == 'createArmIKFK'  ): 
        createIKFK()
    if ( rigSystemFunction == 'createLegIK'  ):
        chooseOrientation()
    if ( rigSystemFunction == 'createShoulderIK' ): 
        createShoulderIK()
    if ( rigSystemFunction == 'getFKControls' ): 
        getFKControls() 
    if ( rigSystemFunction == 'getOneSimpleFK' ): 
        oneSimpleFK()   
    if ( rigSystemFunction == 'createSplineIKFK' ): 
        createSplineIKFK() 
        
def ziltzRigTool_UI(): 
    setRootNaming()

    ##################
    # Layout of UI
    mainWindow = cmds.window(title="Auto Rig Generator 9000")

    column = cmds.columnLayout (width = 200, adjustableColumn=True, columnAttach=('both', 15) ,
                        columnAlign="center", rowSpacing=12 )
    # Welcome and name
    cmds.text( label='Welcome to the Auto Rig! :)', bgc=[1,1,1] ) 
    cmds.text( label='Name of creature/character', fn='obliqueLabelFont', bgc=[1,1,0]  )
    global prefixText
    prefixText = cmds.textField( )
    cmds.button( label='Assign Name', command='assignPrefixName()', bgc=[0,1,1] )

    ##############
    # Create Joints Section
    cmds.text( label='Create Joints', fn='obliqueLabelFont', bgc=[1,1,0]  )
    jointTypeMenu = cmds.optionMenuGrp( mainWindow, label='Joint Type', 
                        changeCommand=chooseJointCreation, adj=2 ) 
    cmds.menuItem( label='Shoulder' ) 
    cmds.menuItem( label='Arm' ) 
    cmds.menuItem( label='Leg' )
    #cmds.button( label='Create Shoulder', command='createShoulderJoints()', bgc=[0,1,1] )
    #cmds.button( label='Create Arm/Leg', command='createArmJoints()', bgc=[0,1,1] )
    #cmds.button( label='Create Foot', command='createFoot()', bgc=[0,1,1] )
    cmds.button( label='Create Joints', command='createJointType()', bgc=[0,1,1] )
    cmds.button( label='Finish placing joints', command='cleanUpLoc()', bgc=[0,0.5,1] )
    
    ##################
    # Joint Setup Section
    cmds.text( label='Joint Setup', fn='obliqueLabelFont', bgc=[1,1,0]  )
    global jointTextBox
    jointTextBox = cmds.textField( )
    cmds.button( label='^^^ Get Joint ^^^', command='fillTextBox(jointTextBox)', bgc=[0,1,1] ) 
    cmds.button( label='Orient Joints', command='orientJoints()', bgc=[0,1,1] ) 
    cmds.button( label='Mirror Joints', command='mirrorJoints()', bgc=[0,1,1] )
    
    ##################
    # Joint Type Section
    cmds.text( label='Name type of joint (i.e. leftArm)', fn='obliqueLabelFont', bgc=[1,1,0]  )
    global ikfk_switchName
    ikfk_switchName = cmds.textField( )
    ##################
    # Create Controls Section
    cmds.text( label='Create Controls', fn='obliqueLabelFont', bgc=[1,1,0]  )
    cmds.optionMenuGrp( label='Rig System', changeCommand=chooseRigSystem, adj=2 ) 
    cmds.menuItem( label='Arm IK / FK System' )
    cmds.menuItem( label='Leg IK System' )
    cmds.menuItem( label='Shoulder IK' ) 
    cmds.menuItem( label='Simple FK' )
    cmds.menuItem( label='One Simple FK' )
    cmds.menuItem( label='Spline IK FK' )
    #cmds.button( label='Create IK and FK Systems', command='createIKFK()', bgc=[0,1,1] )
    #cmds.button( label='Create Shoulder IK', command='createShoulderIK()', bgc=[0,1,1] )
    #cmds.button( label='Create Simple FK', command='getFKControls()', bgc=[0,1,1] )
    #cmds.button( label='Create Stretchy Spline IK', command='createSplineFK()', bgc=[0,1,1] )
    cmds.button( label='Create Rig System', command='createRigSystem()', bgc=[0,1,1] )
    
    #####
    # Extra gadgets
    cmds.text( label='Extra Tools', fn='obliqueLabelFont', bgc=[1,1,0]  )
    cmds.button( label='Display Local Axes', command='displayLocalAxes()', bgc=[0,0.5,1] )
    ##################
    """ 

    cmds.frameLayout( labelVisible=False )
    panel = cmds.outlinerPanel()
    outliner = cmds.outlinerPanel(panel, query=True,outlinerEditor=True)
    cmds.outlinerEditor( outliner, edit=True, mainListConnection='worldList', selectionConnection='modelList', showShapes=False, showReferenceNodes=False, showReferenceMembers=False, showAttributes=False, showConnected=False, showAnimCurvesOnly=False, autoExpand=False, showDagOnly=True, ignoreDagHierarchy=False, 
                        expandConnections=False, showCompounds=True, showNumericAttrsOnly=False, highlightActive=True, autoSelectNewObjects=False, doNotSelectNewObjects=False, transmitFilters=False, showSetMembers=True, setFilter='defaultSetFilter' )
    
    """
    #cmds.menuItem(parent=(jointTypeMenu +'|OptionMenu'))
    # Show window
    #allowedAreas = ['right', 'left']
    #cmds.dockControl( area='left', content=mainWindow, allowedArea=allowedAreas )
    cmds.showWindow( mainWindow )
    
ziltzRigTool_UI()
setRootNaming()


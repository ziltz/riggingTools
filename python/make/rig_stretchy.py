__author__ = 'Jerry'





def rig_makeStretchy( startName, endName, start, end, parent):
	startLoc = rig_transform(0, name=startName, type='locator',
	                             parent=parent, target=start).object
	endLoc = rig_transform(0, name=endName, type='locator',
	                           parent=parent, target=end).object

	pm.parentConstraint(kneeIK, wristBallLoc, mo=True)
	pm.parentConstraint(footBallControl.con, fngBallLoc, mo=True)

	footBallAimTop = mm.eval('rig_makePiston("' + wristBallLoc + '", "' + fngBallLoc + '", "' + side + '_footBallAim");')
	pm.parent(side + '_footBallAim_LOCUp', side + '_toesBallAim_LOCAimOffset')

	pm.orientConstraint(side + '_footBallAim_JNT', footIK, mo=True)

	pm.parent(footBallAimTop, parent)

	return footBallAimTop




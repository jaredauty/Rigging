import maya.cmds as cmds

import ErrorChecking as error
import RiggingControls as rc
import RiggingGroups as rg
reload(error)
reload(rc)
reload(rg)

def generateAutoClav(_name, _shoulderSDK, _wristIK):
	print "doing something"
	error.assertString(_name)
	error.assertMayaObject(_shoulderSDK)
	error.assertMayaObject(_wristIK)
	cmds.select(clear=True)

	# Create joints
	joint1 = cmds.joint(n="%s_IK_JNT" %(_name))
	rc.copyTranslation(joint1, _shoulderSDK)
	joint2 = cmds.joint(n="%s_IKEND_JNT" %(_name))
	rc.copyTranslation(joint2, _wristIK)
	#cmds.parent(joint2, joint1)

	# Create IK
	ikControl = cmds.ikHandle(
		n="%s_IK" %(_name),
		sol="ikRPsolver",
		sj= joint1,
		ee=joint2
		)[0]
	# deselect so we don't get warnings
	cmds.select(d=1)

	# Create pole vec
	locator = cmds.spaceLocator(n="%s_up_LOC" %(_name))[0]
	rc.orientControl(locator, _wristIK)
	locGroup = rg.addGroup(locator, "%s_0" %(locator))
	cmds.setAttr("%s.ty" %(locator), 2)

	cmds.poleVectorConstraint(locator, ikControl)

	# Connect up to rig
	cmds.pointConstraint(_wristIK, locGroup, mo=1)
	cmds.pointConstraint(_wristIK, ikControl, mo=1)

	cmds.orientConstraint(joint1, _shoulderSDK, mo=1)

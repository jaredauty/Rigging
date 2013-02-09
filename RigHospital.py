""" Module for adjusting rigs after generation. This contains methods of renaming, control swapping etc"""
import maya.cmds as cmds
import ErrorChecking as error
reload(error)

def renameControls(_renameMap):
	error.assertStringDict(_renameMap)
	errorString = []
	for control in _renameMap:
		#Check that it exists
		if cmds.objExists(control):
			actualName = cmds.rename(control, _renameMap[control])
			if actualName != _renameMap[control]:
				errorString.append(
					"Error -- Couldn't rename %s to %s, instead renamed to %s" \
						%(control, _renameMap[control], actualName))
		else:
			errorString.append("Error -- Can't find%s\n" %(control))
	print "".join(errorString)

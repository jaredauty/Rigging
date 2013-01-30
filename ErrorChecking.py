""" List of methods for error checking"""

import maya.cmds as cmds

def assertType(_object, _typeExamples):
	if type(_typeExamples) == type([]):
		# could be trying to test against empty list
		if(_typeExamples):
			test = False
			for example in _typeExamples:
				if (type(_object) == type(example)):
					test = True
					break
			assert test, "%s is not of any specified types" %(str(_object))
		else:
			assert type(_object) == type([]), "_object is not of type _typeExamples"
	else:
		assert type(_object) == type(_typeExamples), "_object is not of type _typeExample"

def assertList(_list, _typeExamples):
	# Each member of the list must be one of the types in _typeExamples
	assert type(_list) == type([]), "_list must be a list"
	for obj in _list:
		assertType(obj, _typeExamples)

def assertMayaType(_object, _type):
	assertType(_object, ["", u''])
	assertType(_type, ["", u''])
	assert cmds.objectType(_object, isType = _type), "%s is not of type %s" %(_object, _type)

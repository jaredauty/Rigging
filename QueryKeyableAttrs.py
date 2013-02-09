import maya.cmds as cmds
import pickle
sel = cmds.ls(selection=1)
allKeyableAttrs = []
allControls = {}
questionableAttrs = []
for obj in sel:
    attrs = cmds.listAttr(obj, k=1)
    allControls[obj] = attrs
    for attr in attrs:
        if attr == "scaleX":
            questionableAttrs.append("%s.%s" %(obj, attr))
        if attr == "visibility":
            questionableAttrs.append("%s.%s" %(obj, attr))
        
        allKeyableAttrs.append("%s.%s" %(obj, attr))
"""
for key, value in allControls.items():
    print "\n// -- %s -- //" %(key)
    for attr in value:
        print "\t%s" %(attr)
""" 
if questionableAttrs:
    print "//---- What about these? ----//"
    for attr in questionableAttrs:
        print attr

pickle.dump(allControls, open("rigData/characterSet.dat", "wb"))
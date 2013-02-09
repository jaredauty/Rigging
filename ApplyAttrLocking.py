# Test everything and clean up 

allControls = pickle.load(open("jesseControls.dat", "rb"))

for key, value in allControls.items():
    print "\n// -- %s -- //" %(key)
    for attr in value:
        print "\t%s" %(attr)

def applyControlChange(_control, _attrs):
    #First check that the control exists
    if cmds.objExists(_control):
        # Make sure all new attrs are visible and unlocked
        for attr in _attrs:
            cmds.setAttr("%s.%s" %(_control, attr), l=False, k=1)
        # get current list of attrs
        currentAttrs = cmds.listAttr(_control, k=1)
        # go through and make sure all ones that aren't in _attrs are remove
        for visibleAttr in currentAttrs:
            if visibleAttr not in _attrs:
                cmds.setAttr("%s.%s" %(_control, visibleAttr), l=1, k=0)
        
    else:
        print "Error!!! couldn't find %s" %(_control)

# Try out the first one
applyControlChange("arm_R_FK_upperArm_CTRL", allControls["arm_R_FK_upperArm_CTRL"])

# Apply changes
for key, value in allControls.items():
    applyControlChange(key, value)

#Check changes
newControls = {}
for obj in sel:
    attrs = cmds.listAttr(obj, k=1)
    newControls[obj] = attrs

status = True
for key, value in newControls.items():
    #check that key is in original
    if key not in allControls:
        print "Error !!!, %s is not in allControls" %(key)
        status = False
    else:
        #check that attr list are the same
        if len(value) != len(allControls[key]):
            print "Error!!! wrong number of attrs on %s" %(key)
            status = False
        else:
            for attr in value:
                if attr not in allControls[key]:
                    status = False
                    print "Error!!! %s should not be on %s" %(attr, key)
if status:
    print "Ran like a bous!"

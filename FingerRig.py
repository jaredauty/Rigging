"""
A script that takes in a list of joints representing the hand and then creates
a control rig for the hand.
"""

import maya.cmds as cmds
import RiggingControls as rc
import RiggingGroups as rg
reload(rg)
reload(rc)

class FingerRig:
    def __init__(
            self,
            _name,
            _joints,
            _isThumb = False
            ):
        self.m_name = _name
        self.m_group = cmds.group(n="%s_GRP" %(self.m_name), em=True)
        self.m_isThumb = _isThumb
        if self.m_isThumb:
            assert len(_joints) == 4, "Wrong number of joints" 
        else:
            assert len(_joints) == 5, "Wrong number of joints" 
        self.m_joints = _joints
        self.m_isGenerated = True

    def getUpperSDK(self):
        assert self.m_isGenerated, "Rig not generated"
        return cmds.listRelatives(self.m_controls[0], p=1)[0]

    def getUpperLength(self):
        assert self.m_isGenerated, "Rig not generated"
        return rc.getDistBetween(self.m_controls[0], self.m_controls[1])

    def getKnuckle(self):
        assert self.m_isGenerated, "Rig not generated"
        return self.m_controls[1]

    def getGroup(self):
        return self.m_group

    def generate(self):
        if self.m_isThumb:
            names = ["metacarpal", "knuckle", "tip", "tipEND"]
        else:
            names = ["metacarpal", "knuckle", "mid", "tip", "tipEND"]
        i = 0
        parentControl = False
        self.m_controls = []
        self.m_stretchControls = []
            
        for joint in self.m_joints:
            # Create control
            newStretch = False
            if joint != self.m_joints[0]:
                #Create stretch control
                stretchName = "%s_%s_stretch_CTRL" %(self.m_name, names[i])
                newStretch = cmds.spaceLocator(n=stretchName)[0]
                rc.setMultiAttrs(
                    newStretch,
                    ["localScaleX", "localScaleY", "localScaleZ"],
                    0.15
                    )
                rc.orientControl(newStretch, cmds.listRelatives(joint, p=1)[0])
                rc.copyTranslation(newStretch, joint)
                if parentControl:
                    cmds.parent(newStretch, parentControl)
                else:
                    cmds.parent(newStretch, self.m_group)
                rg.add3Groups(
                    newStretch, 
                    ["_SDK", "_CONST", "_0"]
                    )
                # lock unused attrs
                rc.lockAttrs(
                    newStretch,
                    ["ty", "tz", "rotate", "scale"],
                    True,
                    False
                    )
                parentControl = newStretch
            
            if joint != self.m_joints[-1]:
                controlName = "%s_%s_CTRL" %(self.m_name, names[i])
                newControl = cmds.circle(
                    n=controlName,
                    nr=(1, 0, 0),
                    r=0.1
                    )[0]
                rc.orientControl(newControl, joint)
                if parentControl:
                    cmds.parent(newControl, parentControl)
                else:
                    cmds.parent(newControl, self.m_group)
                self.m_controls.append(newControl)

                groups = rg.add3Groups(newControl, ["_SDK", "_CONST", "_0"])
                if newStretch:
                    # Attach to stretch
                    cmds.parentConstraint(newStretch, groups[1], mo=1)
                # Attach to joint
                cmds.parentConstraint(newControl, joint, mo=1)
                rc.lockAttrs(
                    newControl,
                    ["translate", "scale"],
                    True,
                    False
                    )
                parentControl = newControl
                i += 1
            else:
                cmds.parentConstraint(newStretch, joint, mo=1)

        # Rig metacarpals
        if not self.m_isThumb:
            pass

        self.m_isGenerated = True
        

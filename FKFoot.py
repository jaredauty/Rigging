""" Script to generate a simple FK foot control system"""

import maya.cmds as cmds
import RiggingControls as rc
import RiggingGroups as rg
reload(rc)
reload(rg)


class FKFootRig:
    def __init__(
            self,
            _name,
            _joints,
            _footMain,
            _parent
            ):
        self.m_name = _name
        self.m_group = cmds.group(n="%s_GRP" %(self.m_name), em=True)
        self.m_joints = _joints
        self.m_footMain = _footMain
        self.m_parent = _parent
        jointGroup = rg.addGroup(self.m_joints[0], "%s_0" %(self.m_joints[0]))
        cmds.parent(jointGroup, self.m_group)
        self.m_ankleGenerated = False
        self.m_toeGenerated = False

    def generate(self):
        self.createAnkle()
        self.createToe()
    
    def getGroup(self):
        return self.m_group

    def createAnkle(self):
        self.m_ankleCtrl = cmds.circle(
            n="%s_ankle_CTRL" %(self.m_name),
            nr=(0, 1, 0)
            )[0]
        rc.orientControl(self.m_ankleCtrl, self.m_footMain)
        groups = rg.add3Groups(self.m_ankleCtrl, ["_SDK", "_CONST", "_0"])
        cmds.parentConstraint(self.m_ankleCtrl, self.m_joints[0], mo = True)
        cmds.parent(groups[-1], self.m_group)
        # Parent to parent
        cmds.parentConstraint(self.m_parent, groups[1], mo=1)
        self.m_ankleGenerated = True

        #Lock unused attributes
        rc.lockAttrs(self.m_ankleCtrl, ["translate", "scale"], True, False)

    def createToe(self):
        if not self.m_ankleGenerated:
            self.createAnkle()
        self.m_toeCtrl = cmds.circle(
            n="%s_toe_CTRL" %(self.m_name),
            nr=(1, 0, 0)
            )[0]
        rc.orientControl(self.m_toeCtrl, self.m_joints[1])
        groups = rg.add3Groups(self.m_toeCtrl, ["_SDK", "_CONST", "_0"])
        cmds.parentConstraint(self.m_toeCtrl, self.m_joints[1])
        cmds.parent(groups[-1], self.m_ankleCtrl)

        self.m_toeGenerated = True
        #Lock unused attributes
        rc.lockAttrs(self.m_toeCtrl, ["translate", "scale"], True, False)

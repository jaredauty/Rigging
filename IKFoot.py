""" Script to generate a simple IK foot control system"""

import maya.cmds as cmds
import RiggingControls as rc
import RiggingGroups as rg
reload(rc)
reload(rg)

class IKFootRig:
    def __init__(
            self, 
            _name,
            _joints,
            _toePivot,
            _heelPivot,
            _insidePivot,
            _outsidePivot,
            _footMain,
            _ankleIK
            ):
        self.m_name = _name
        self.m_group = cmds.group(n="%s_GRP" %(self.m_name), em=True)
        self.m_joints = _joints
        jointGroup = rg.addGroup(self.m_joints[0], "%s_0" %(self.m_joints[0]))
        cmds.parent(jointGroup, self.m_group)
        self.m_toePivotLoc = _toePivot
        self.m_heelPivotLoc = _heelPivot
        self.m_insidePivotLoc = _insidePivot
        self.m_outsidePivotLoc = _outsidePivot
        self.m_footMainLoc = _footMain
        self.m_ankleIK = _ankleIK

    def getGroup(self):
        return self.m_group

    def generate(self):
        # Generate controls
        self.m_heelRoll = cmds.spaceLocator(
            n="%s_heelRoll_CTRL" %(self.m_name)
            )[0]
        self.m_insideRoll = cmds.spaceLocator(
            n="%s_insideRoll_CTRL" %(self.m_name)
            )[0]
        self.m_outsideRoll = cmds.spaceLocator(
            n="%s_outsideRoll_CTRL" %(self.m_name)
            )[0]
        self.m_toeRoll = cmds.spaceLocator(
            n="%s_toeRoll_CTRL" %(self.m_name)
            )[0]
        self.m_ballRoll = cmds.spaceLocator(
            n="%s_ballRoll_CTRL" %(self.m_name)
            )[0]
        self.m_toeFlap = cmds.spaceLocator(
            n="%s_toeFlap_CTRL" %(self.m_name)
            )[0]
        
        self.m_mainCtrl = cmds.circle(
            n="%s_main_CTRL" %(self.m_name),
            nr=(1, 0, 0)
            )[0]
        rc.orientControl(self.m_mainCtrl, self.m_footMainLoc)
        cmds.parent(self.m_mainCtrl, self.m_group)
        mainCtrlGroups = rg.add3Groups(
            self.m_mainCtrl, 
            ["_SDK", "_CONST", "_0"]
            )
        # Move everything into the right places
        rc.orientControl(self.m_heelRoll, self.m_heelPivotLoc)
        rc.orientControl(self.m_insideRoll, self.m_insidePivotLoc)
        rc.orientControl(self.m_outsideRoll, self.m_outsidePivotLoc)
        rc.orientControl(self.m_toeRoll, self.m_toePivotLoc)
        rc.orientControl(self.m_ballRoll, self.m_joints[1])
        rc.orientControl(self.m_toeFlap, self.m_joints[1])



        # Parent everything
        cmds.parent(self.m_heelRoll, self.m_mainCtrl)
        cmds.parent(self.m_insideRoll, self.m_heelRoll)
        cmds.parent(self.m_outsideRoll, self.m_insideRoll)
        cmds.parent(self.m_toeRoll, self.m_outsideRoll)
        cmds.parent(self.m_ballRoll, self.m_toeRoll)
        cmds.parent(self.m_toeFlap, self.m_toeRoll)

        # Create Groups above
        defaultExt = ["_SDK", "_CONST", "_0"]
        rg.add3Groups(self.m_heelRoll, defaultExt)
        rg.add3Groups(self.m_insideRoll, defaultExt)
        rg.add3Groups(self.m_outsideRoll, defaultExt)
        rg.add3Groups(self.m_toeRoll, defaultExt)
        rg.add3Groups(self.m_ballRoll, defaultExt)
        rg.add3Groups(self.m_toeFlap, defaultExt)

        # Create IKs
        self.m_footIK = cmds.ikHandle(
            sj=self.m_joints[0],
            ee=self.m_joints[1],
            sol="ikRPsolver"
            )[0]
        cmds.parent(self.m_footIK, self.m_ballRoll)
        self.m_toeIK = cmds.ikHandle(
            sj=self.m_joints[1],
            ee=self.m_joints[2],
            sol="ikRPsolver"
            )[0]
        cmds.parent(self.m_toeIK, self.m_toeFlap)

        # Sort ankle
        cmds.parentConstraint(self.m_ballRoll, self.m_ankleIK, mo=True)
        cmds.parentConstraint(self.m_ankleIK, self.m_joints[0], mo=True)
    
    def duplicateJoints(self, _topJoint):
        dupJoints = cmds.duplicate(_topJoint, rc=True)
        i = 0
        for name in [
                "%s_IK_ankle_JNT" %(self.m_name), 
                "%s_IK_ball_JNT" %(self.m_name),
                "%s_IK_toeEND_JNT"%(self.m_name)
                ]: 
            cmds.rename(dupJoints[i], name)
            dupJoints[i] = name
            i+=1
        return dupJoints



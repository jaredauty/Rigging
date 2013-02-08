""" Script to generate a leg rig with IK FK switching. This script uses the \
    ArmRig class and the FootRig class and combines them. """

import maya.cmds as cmds
import FootRig as fr
import ArmRig as arm
import RiggingControls as rc
reload(fr)
reload(arm)
reload(rc)

class LegRig:
    def __init__(
            self,
            _sceneData,
            _name,
            _baseName,
            _legJoints,
            _footJoints,
            _toePivot,
            _heelPivot,
            _insidePivot,
            _outsidePivot,
            _footMain,
            _twistAxis="y"
            ):
        self.m_sceneData = _sceneData
        self.m_name = _name
        self.m_baseName = _baseName
        self.m_group = "%s_GRP" %(self.m_name)
        if not cmds.objExists(self.m_group):
            self.m_group = cmds.group(n=self.m_group, em=True)
        self.m_legJoints = _legJoints#self.duplicateLegJoints(_legJoints)
        self.m_footJoints = _footJoints#self.duplicateFootJoints( _footJoints)
        self.m_toePivot = _toePivot
        self.m_heelPivot = _heelPivot
        self.m_insidePivot = _insidePivot
        self.m_outsidePivot = _outsidePivot
        self.m_footMain = _footMain
        self.m_twistAxis = _twistAxis
        self.m_allControls = {}
        # stretch chain parameters
        self.m_numUpperControls = 2
        self.m_numLowerControls = 2
        self.m_numUpperJoints = 5
        self.m_numLowerJoints = 5
        self.m_upperStretchJoints = False
        self.m_lowerStretchJoints = False

    def setUpperStretchChain(
            self,
            _numControls,
            _joints,
            _numJoints = 0
            ):
        self.m_numUpperControls = _numControls
        if _joints:
            self.m_upperStretchJoints = _joints
            self.m_numUpperJoints = len(_joints)
        else:
            self.m_numUpperJoints = _numJoints

    def setLowerStretchChain(
            self,
            _numControls,
            _joints,
            _numJoints = 0
            ):
        self.m_numLowerControls = _numControls
        if _joints:
            self.m_lowerStretchJoints = _joints
            self.m_numLowerJoints = len(_joints)
        else:
            self.m_numLowerJoints = _numJoints

    def getAllControls(self):
        return self.m_allControls

    def getGroup(self):
        return self.m_group

    def generate(self):
        # Generate Leg
        self.m_legRig = arm.ArmRig(
            self.m_sceneData,
            self.m_legJoints, 
            self.m_name,
            self.m_baseName,
            self.m_twistAxis,
            False
            )
        self.m_legRig.setUpperStretchChain(
            self.m_numUpperControls,
            self.m_upperStretchJoints,
            self.m_numUpperJoints
            )
        self.m_legRig.setLowerStretchChain(
            self.m_numLowerControls,
            self.m_lowerStretchJoints,
            self.m_numLowerJoints
            )
        self.m_legRig.generate()
        rc.addDictToControlDict(self.m_allControls, self.m_legRig.getAllControls())

        # Generate Foot
        self.m_footRig = fr.FootRig(
            self.m_sceneData,
            "%s_foot" %(self.m_name),
            self.m_baseName,
            self.m_footJoints[0],
            self.m_toePivot,
            self.m_heelPivot,
            self.m_insidePivot,
            self.m_outsidePivot,
            self.m_footMain,
            self.m_legRig.getIKControl(),
            self.m_legRig.getFKParent(),
            self.m_legRig.getBINDParent(),
            self.m_legRig.getAnkleTwist(),
            self.m_legRig.getBlendControl()
            )
        self.m_footRig.generate()
        rc.addDictToControlDict(self.m_allControls, self.m_footRig.getAllControls())
        cmds.parent(self.m_footRig.getGroup(), self.m_group)

        #Rig blend control
        self.m_legRig.rigBlendControl(self.m_footRig.getAnkleJoint())

        # Connect up visibility
        ikVis, fkVis = self.m_legRig.getVisibilityAttrs()
        cmds.connectAttr(
            ikVis,
            "%s.visibility" %(self.m_footRig.m_ikFoot.getGroup())
            )
        cmds.connectAttr(
            fkVis,
            "%s.visibility" %(self.m_footRig.m_fkFoot.getGroup())
            )

    def duplicateLegJoints(self, _joints):
        dupJoints = cmds.duplicate(_joints[0], rc=True)
        i = 0
        for name in [
                "%s_hip_JNT" %(self.m_name),
                "%s_knee1_JNT" %(self.m_name),
                "%s_knee2_JNT" %(self.m_name),
                "%s_legAnkle_JNT" %(self.m_name)
                ]:
            cmds.rename(dupJoints[i], name)
            dupJoints[i] = name
            i+=1
        return dupJoints

    def duplicateFootJoints(self, _joints):
        dupJoints = cmds.duplicate(_joints[0], rc=True)
        i = 0
        for name in [
                "%s_footAnkle_JNT" %(self.m_name),
                "%s_ball_JNT" %(self.m_name),
                "%s_toeEnd_JNT" %(self.m_name)
                ]:
            cmds.rename(dupJoints[i], name)
            dupJoints[i] = name
            i+=1
        return dupJoints

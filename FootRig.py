""" Script to generate a foot rig with IK FK switching """
import maya.cmds as cmds
import IKFoot
import FKFoot
import RiggingGroups as rg
import RiggingControls as rc
reload(IKFoot)
reload(FKFoot)
reload(rg)
reload(rc)

class FootRig:
    def __init__(
            self, 
            _sceneData,
            _name, 
            _topJoint,
            _toePivot,
            _heelPivot,
            _insidePivot,
            _outsidePivot,
            _footMain,
            _ankleIK,
            _parentFK,
            _parentBIND,
            _parentTwist,
            _blendControl = False,
            _blendAttr = "IK_FK_Blend"
            ):
        self.m_sceneData = _sceneData
        self.m_name = _name
        self.m_group = cmds.group(n="%s_GRP" %(self.m_name), em=True)
        self.m_topJoint = _topJoint
        self.m_footToePivot = _toePivot
        self.m_footHeelPivot = _heelPivot
        self.m_footInsidePivot = _insidePivot
        self.m_footOutsidePivot = _outsidePivot
        self.m_footMain = _footMain
        self.m_ankleIK = _ankleIK
        self.m_parentFK = _parentFK
        self.m_parentBIND = _parentBIND
        self.m_parentTwist = _parentTwist
        self.m_blendAttr = _blendAttr
        if _blendControl:
            self.m_blendControl = _blendControl
        else:
            self.m_blendControl = cmds.circle(
                n="%s_blend_CTRL" %(self.m_name),
                )[0]
            cmds.parent(self.m_blendControl, self.m_group)
        if not cmds.objExists(
                "%s.%s" %(self.m_blendControl, self.m_blendAttr
                )):
            print "add attr"
            cmds.addAttr(
                self.m_blendControl,
                ln=self.m_blendAttr,
                at="float",
                min = 0,
                max = 1,
                dv = 0,
                k=1
                )
        
    def getGroup(self):
        return self.m_group

    def generate(self):
        # Create IK
        self.m_ikJoints = self.duplicateJoints(self.m_topJoint, "IK")
        rc.addToLayer(self.m_sceneData, "ref", self.m_ikJoints[0])
        self.m_ikFoot = IKFoot.IKFootRig(
            self.m_sceneData,
            "%s_IK" %(self.m_name),
            self.m_ikJoints,
            self.m_footToePivot,
            self.m_footHeelPivot,
            self.m_footInsidePivot,
            self.m_footOutsidePivot,
            self.m_footMain,
            self.m_ankleIK
            )
        self.m_ikFoot.generate()
        cmds.parent(self.m_ikFoot.getGroup(), self.m_group)

        # Create FK
        self.m_fkJoints = self.duplicateJoints(self.m_topJoint, "FK")
        rc.addToLayer(self.m_sceneData, "ref", self.m_fkJoints[0])
        self.m_fkFoot = FKFoot.FKFootRig(
            self.m_sceneData,
            "%s_FK" %(self.m_name),
            self.m_fkJoints,
            self.m_footMain,
            self.m_parentFK
            )
        self.m_fkFoot.generate()
        cmds.parent(self.m_fkFoot.getGroup(), self.m_group)

        # Create BIND
        self.m_bindJoints = self.duplicateJoints(
            self.m_topJoint,
            "BIND"
            )
        rc.addToLayer(self.m_sceneData, "ref", self.m_bindJoints[0])
        bindGroups = rg.add3Groups(
            self.m_bindJoints[0],
            ["_SDK", "_CONST", "_0"]
            )
        cmds.parent(bindGroups[-1], self.m_group)
        self.connectBind()
        # connect to parent
        cmds.parentConstraint(self.m_parentBIND, bindGroups[-1], mo=1)
        # connect to parent twist
        # Strip constraint
        targetList = cmds.parentConstraint(self.m_parentTwist, q=1, tl=1)
        cmds.parentConstraint(targetList, self.m_parentTwist, e=True, rm=True)
        # Add new constraint
        cmds.parentConstraint(self.m_bindJoints[0], self.m_parentTwist, mo=1)

    def connectBind(self):
        #Create opposite node to blend
        blendOpposite = rc.create1MinusNode(
            "%s.%s" %(self.m_blendControl, self.m_blendAttr),
            "%s_IKFKBlendOpp_CTRL" %(self.m_name)
            )
        for i in range(len(self.m_bindJoints)):
            const1 = cmds.parentConstraint(
                self.m_ikJoints[i],
                self.m_bindJoints[i],
                st = ["x", "y", "z"]
                )[0]
            const2 = cmds.parentConstraint(
                self.m_fkJoints[i],
                self.m_bindJoints[i],
                st = ["x", "y", "z"]
                )[0]
            cmds.connectAttr(
                blendOpposite,
                "%s.blendParent2" %(self.m_bindJoints[i])
                )
            # Change to quarternion
            pairBlend = cmds.listConnections(
                "%s.constraintRotateX" %(const1),
                d=1
                )[0]
            cmds.setAttr("%s.rotInterpolation" %(pairBlend), 1)
        
    def duplicateJoints(self, _topJoint, _tagName):
         dupJoints = cmds.duplicate(_topJoint, rc=True)
         i = 0
         for name in [
                 "%s_%s_ankle_JNT" %(self.m_name, _tagName),
                 "%s_%s_ball_JNT" %(self.m_name, _tagName),
                 "%s_%s_toeEND_JNT"%(self.m_name, _tagName)
                 ]:
             cmds.rename(dupJoints[i], name)
             dupJoints[i] = name
             i+=1
         return dupJoints


import maya.cmds as cmds

#contains all of the group based rigging procedures

#static Default Values of group name extensions

s_defaultExt1 = "_SDK"
s_defaultExt2 = "_CONST"
s_defaultExt3 = "_0"


#--------------TOP LEVEL-------------#    
#these are procedures that are attached buttons

#adds the default 3 groups above the item selected

def addDefaultGroups():
    selection = cmds.ls(selection=True)
    for i in selection:
        addGroup(i, i+s_defaultExt1)
        addGroup(i+s_defaultExt1, i+s_defaultExt2)
        addGroup(i+s_defaultExt2, i+s_defaultExt3)

#adds a single group above an object

def addSingleGroup(_selection, _ext = False):
    if not _ext:
       _ext = getExt()
    
    #check that the user has entered an extension
    if (_ext != ""):
        for i in _selection:
            addGroup(i, i+_ext)
    
    #otherwise tell the user to enter an extension
    
    else:
        print "Button not Activated: Valid Extension Required"
        
#adds 3 groups above an object

def add3Groups(_sel, _ext = False):
    groups = []
    if not _ext:
        _ext = getExtFromUser()
    groups.append(addGroup(_sel, _sel+_ext[0]))
    groups.append(addGroup(_sel+_ext[0], _sel+_ext[1]))
    groups.append(addGroup(_sel+_ext[1], _sel+_ext[2]))
    return groups
#--------------Low Level-------------#
#these are low level procedures that are not directly
#attached to a button, but used by the ones that are

#adds a group above the _item with the name, _GroupName.
#it aligns the group to the item it is above in the hierarchy

def addGroup(_item, _groupName):
    itemParent = cmds.listRelatives(_item, p=1)
    cmds.group(em=True, n=_groupName, parent=_item)
    cmds.parent(_item+"|"+_groupName, world=True)
    cmds.parent(_item, _groupName)
    if itemParent:
        cmds.parent(_groupName, itemParent)
    return _groupName

def getExtFromUser():
        #get the desired extension
    Ext = ["","",""]
    Ext [0] = getExt()
    
    # only run the next command if a valid extension has been entered
    
    if (Ext[0] != ""):
        Ext [1] = getExt()
        
        #only run the next command if a valid extension was entered
        
        if (Ext[1] != ""):
            Ext [2] = getExt()
    
    #check that the user has entered all required extensions
    
    if (Ext[0] != "" and Ext[1] != "" and Ext[2] != ""):
    
        #then check that The extensions are different
        
        if (Ext[0] != Ext[2] and Ext[1] != Ext[0] and Ext[2] != Ext[1]):
            return Ext
        else:
            #error message if the extensions are the same
            
            print "Button not Activated: Extensions Must be Unique"    
    else:
        #error message if cancel was pressed or an empty extension entered
    
        print "Button not Activated: Valid Extension Required"
    return False
#a procedure which generates a pop up window to get the desired 
#extension to be added to a group

def getExt():
    result = cmds.promptDialog(
                title='Extension',
                message='Enter Desired Extension:',
                button=['Enter', 'Cancel'],
                defaultButton='Enter',
                cancelButton='Cancel',
                dismissString='Cancel')
    
    text = ""
    if result == 'Enter':
        text = cmds.promptDialog(query=True, text=True)
        
    return text
# Strip everything between underscores number _front and _back
def stripMiddle(_string, _front = 0, _back = 0):
    newString = _string
    for i in range(_front):
        newString = newString[newString.find("_")+1:]
    for i in range(_back):
        newString = newString[:newString.rfind("_")]
    return newString

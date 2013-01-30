
""" Basic class for holding scene data that rigs may need to query"""
import ErrorChecking as error
reload(error)

class SceneData:
	def __init__(self, _hiddenLyr, _refLyr, _mainCtrlLyr, _detailCtrlLyr):
		error.assertMayaType(_hiddenLyr, "displayLayer")
		error.assertMayaType(_refLyr, "displayLayer")
		error.assertMayaType(_mainCtrlLyr, "displayLayer")
		error.assertMayaType(_detailCtrlLyr, "displayLayer")
		self.m_hiddenLyr = _hiddenLyr
		self.m_refLyr = _refLyr
		self.m_mainCtrlLyr = _mainCtrlLyr
		self.m_detailCtrlLyr = _detailCtrlLyr
		self.m_setDictionary = {}


	def addSet(self, _set, _identifier):
		error.assertMayaType(_set, "objectSet")
		error.assertString(_identifier)
		self.m_setDictionary[_identifier] = _set

	def getSet(self, _identifier):
		error.assertString(_identifier)
		if _identifier in self.m_setDictionary:
			return self.m_setDictionary[_identifier]
		else:
			return ""

	def getHidden(self):
		return self.m_hiddenLyr

	def getLayer(self, _layerIdentifier):
		if _layerIdentifier == "hidden":
			return self.m_hiddenLyr
		elif _layerIdentifier == "ref":
			return self.m_refLyr
		elif _layerIdentifier == "mainCtrl":
			return self.m_mainCtrlLyr
		elif _layerIdentifier == "detailCtrl":
			return self.m_detailCtrlLyr
		else:
			assert false, "incorrect layer identifier specified!"
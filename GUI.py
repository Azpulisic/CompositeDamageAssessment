from os import path
from meta import *
import DamageAssess
import time

def RefreshWindow():
	currentWindow = windows.Window(active=True)
	currentWindow.delete()
	curWindow = windows.Create3DWindow("MetaPost")
	return curWindow

def GetGeoD3plotPath():
	toolbar_name = "CompositeDamageAssessment"
	textbox_name = "Geometry"
	geoPath = toolbars.TextboxGetValue(toolbar_name, textbox_name)
	if geoPath:
		geoPath = path.abspath(geoPath)
		d3plotPath = path.join(path.dirname(geoPath), "d3plot")
	return geoPath, d3plotPath

def GetInputCriteria():
	toolbar_name = "CompositeDamageAssessment"
	textbox_name = "Specify criteria"
	criteria_name = toolbars.TextboxGetValue(toolbar_name, textbox_name)
	return criteria_name

#加载有限元模型文件
def LoadGeometry():
	curWindow = RefreshWindow()
	geoPath, d3plotPath = GetGeoD3plotPath()
	curModel = models.LoadModel(curWindow.name, geoPath, 'AUTO')
	results.LoadDeformations(curModel.id, d3plotPath, 'AUTO', 'all', 'Displacements')
	DamageAssess.SaveResultSetsCnt(curModel.id)
	return curModel

def Assess():
	startTime = time.time()
	curModel = models.Model(0)
	_, d3plotPath = GetGeoD3plotPath()
	criteria_name = GetInputCriteria()
	DamageAssess.CriterionAssess(curModel, d3plotPath, criteria_name)
	endTime = time.time()

if __name__ == '__main__':
	Assess()



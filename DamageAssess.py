from os import path
from meta import *
import ReadWriteTool
import math

resultSetsCnt = 0

def SaveResultSetsCnt(curModel_id):
	global resultSetsCnt
	resultSetsCnt = results.Resultsets(curModel_id)[-1].subcase

def SetElemsStressAttr(curModel, d3plotPath, elems, stress_type, resultSet):
	trans = {'x':'Stresses,Normal-1(UCS)', 
			'y':'Stresses,Normal-2(UCS)', 
			'xy':'Stresses,Shear-12(UCS)', 
			'yz': 'Stresses,Shear-23(UCS)',
			 'strain_x':'Strains,Normal-X(GCS)',
			 'strain_y':'Strains,Normal-Y(GCS)',
			 'strain_xy':'Strains,Shear-XY(GCS)'}
	results.LoadScalar(curModel.id, d3plotPath, 'AUTO', f'{resultSet.subcase}', trans[stress_type])
	resultSet = results.Resultsets(curModel.id)[resultSet.subcase]
	for elem in elems:
		attrValue = round(ReadWriteTool.ReadScalar(resultSet, elem), 2)
		elem.set_attribute(stress_type, 'numerical', attrValue)

#提取单元应力，并存储在各单元属性中
def SetElemsAttrs(curModel, d3plotPath, resultSet):
	all_materials = materials.Materials(curModel.id)
	for material in all_materials:
		if material.type == 6:
			elems = material.get_elements("all")
			SetElemsStressAttr(curModel, d3plotPath, elems, 'x', resultSet)
			SetElemsStressAttr(curModel, d3plotPath, elems, 'y', resultSet)
			SetElemsStressAttr(curModel, d3plotPath, elems, 'xy', resultSet)
			SetElemsStressAttr(curModel, d3plotPath, elems, 'yz', resultSet)
			SetElemsStressAttr(curModel, d3plotPath, elems, 'strain_x', resultSet)
			SetElemsStressAttr(curModel, d3plotPath, elems, 'strain_y', resultSet)
			SetElemsStressAttr(curModel, d3plotPath, elems, 'strain_xy', resultSet)

def Macaulay(alpha):
	if alpha < 0:
		return 0
	else:
		return alpha

#Hashin
def Hashin(elem, tanBuMatPara):
	#应力应变提取
	sigma_aa = elem.get_attributes('x')['x']
	sigma_bb = elem.get_attributes('y')['y']
	sigma_ab = elem.get_attributes('xy')['xy']
	epsilon_bb = elem.get_attributes('strain_y')['strain_y']
	epsilon_ab = elem.get_attributes('strain_xy')['strain_xy']
	#材料参数提取
	xt = tanBuMatPara['xt']
	xc = tanBuMatPara['xc']
	yt = tanBuMatPara['yt']
	yc = tanBuMatPara['yc']
	sc = tanBuMatPara['sc']
	beta = tanBuMatPara['beta']
	#基体拉伸、压缩
	if sigma_bb >= 0:
		em2 = (sigma_bb / yt) ** 2 + (sigma_ab / sc) ** 2
		ed2 = 0
	else:
		em2 = 0
		ed2 = (sigma_bb / (2 * sc)) ** 2 + ((yc / (2 * sc)) ** 2 - 1) * (sigma_bb / yc) + (sigma_ab / sc) ** 2
	#纤维拉伸、压缩
	if sigma_aa >= 0:
		ef2 = (sigma_aa / xt) ** 2 + beta * (sigma_ab / sc) ** 2
		ec2 = 0
	else:
		ef2 = 0
		if ed2 >= 1:
			xc = 2 * yc
		ec2 = (sigma_aa / xc) ** 2
	return [ef2, ec2, em2, ed2]

#TsaiWu
def TsaiWu(elem, tanBuMatPara):
	#应力应变提取
	sigma_aa = elem.get_attributes('x')['x']
	sigma_bb = elem.get_attributes('y')['y']
	sigma_ab = elem.get_attributes('xy')['xy']
	epsilon_bb = elem.get_attributes('strain_y')['strain_y']
	epsilon_ab = elem.get_attributes('strain_xy')['strain_xy']
	#材料参数提取
	xt = tanBuMatPara['xt']
	xc = tanBuMatPara['xc']
	yt = tanBuMatPara['yt']
	yc = tanBuMatPara['yc']
	sc = tanBuMatPara['sc']
	beta = tanBuMatPara['beta']
	#基体拉伸、压缩
	if sigma_bb >= 0:
		em2 = sigma_bb**2/(yc*yt) + (sigma_ab/sc)**2 +(yc -yt)*sigma_bb/(yc*yt)
		ed2 = 0
	else:
		em2 = 0
		ed2 = sigma_bb**2/(yc*yt) + (sigma_ab/sc)**2 - (yc -yt)*sigma_bb/(yc*yt)
	#纤维拉伸、压缩
	if sigma_aa >= 0:
		ef2 = (sigma_aa / xt) ** 2 + beta * (sigma_ab / sc) ** 2
		ec2 = 0
	else:
		ef2 = 0
		if ed2 >= 1:
			xc = 2 * yc
		ec2 = (sigma_aa / xc) ** 2
	return [ef2, ec2, em2, ed2]

def CriterionAssess(curModel, d3plotPath, criteria_name):
	failure_data_path = path.join(path.dirname(d3plotPath), criteria_name+"Data.txt")
	if path.exists(failure_data_path):
		[dataFT, dataFC, dataMT, dataMC] = ReadWriteTool.ReadData(failure_data_path)
		allElems = elements.Elements(curModel.id)
		ReadWriteTool.create_resultset(criteria_name + "tensile failure", allElems, dataFT, curModel.id)
		ReadWriteTool.create_resultset(criteria_name + "compress failure", allElems, dataFC, curModel.id)
		ReadWriteTool.create_resultset(criteria_name + "tensile failure", allElems, dataMT, curModel.id)
		ReadWriteTool.create_resultset(criteria_name + "compress failure", allElems, dataMC, curModel.id)
	else:
		if criteria_name == "Chang-Chang":
			ChangChangAssess(curModel, d3plotPath, criteria_name)
		elif criteria_name == "Tsai-Wu":
			TsaiWuAssess(curModel, d3plotPath, criteria_name)
		elif criteria_name == "Hashin":
			HashinAssess(curModel, d3plotPath, criteria_name)

#Chang-Chang
def ChangChang(elem, tanBuMatPara, elemVolume):
	#应力应变提取
	sigma_aa = elem.get_attributes('x')['x']
	sigma_bb = elem.get_attributes('y')['y']
	sigma_ab = elem.get_attributes('xy')['xy']
	epsilon_aa = elem.get_attributes('strain_x')['strain_x']
	epsilon_bb = elem.get_attributes('strain_y')['strain_y']
	epsilon_ab = elem.get_attributes('strain_xy')['strain_xy']
	delta_0_ft = elem.get_attributes('delta_0_ft')['delta_0_ft']
	delta_0_fc = elem.get_attributes('delta_0_fc')['delta_0_fc']
	delta_0_mt = elem.get_attributes('delta_0_mt')['delta_0_mt']
	delta_0_mc = elem.get_attributes('delta_0_mc')['delta_0_mc']
	#单元特征长度
	if elemVolume > 0:
		Lc = math.pow(elemVolume, 1/3)
	else:
		return 0
	#材料参数提取
	xt = tanBuMatPara['xt']
	xc = tanBuMatPara['xc']
	yt = tanBuMatPara['yt']
	yc = tanBuMatPara['yc']
	sc = tanBuMatPara['sc']
	delta_f = tanBuMatPara['delta_f']
	beta = tanBuMatPara['beta']
	alpha = tanBuMatPara['alpha']
	#基体拉伸、压缩初始损伤判据
	if sigma_bb >= 0:
		em2 = (sigma_bb / yt) ** 2 + (sigma_ab / sc) ** 2
		ed2 = 0
	else:
		em2 = 0
		ed2 = (sigma_bb / (2 * sc)) ** 2 + ((yc / (2 * sc)) ** 2 - 1) * (sigma_bb / yc) + (sigma_ab / sc) ** 2
	#纤维拉伸、压缩初始损伤判据
	if sigma_aa >= 0:
		ef2 = (sigma_aa / xt) ** 2 + beta * (sigma_ab / sc) ** 2
		ec2 = 0
	else:
		ef2 = 0
		if ed2 >= 1:
			xc = 2 * yc
		ec2 = (sigma_aa / xc) ** 2
	#计算刚度损伤变量
	if ef2 > 1:
		cur_delta = Lc * math.pow(Macaulay(epsilon_aa)**2 + alpha * epsilon_ab**2, 1/2)
		dft = delta_f * (cur_delta - delta_0_ft)/(cur_delta * (delta_f - delta_0_ft))
	else:
		dft = 1
	if ec2 > 1:
		cur_delta = Lc * Macaulay(-epsilon_aa)
		dfc = delta_f * (cur_delta - delta_0_fc)/(cur_delta * (delta_f - delta_0_fc))
	else:
		dfc = 1
	if em2 > 1:
		cur_delta = Lc * math.pow(Macaulay(epsilon_bb)**2 + epsilon_ab**2, 1/2)
		dmt = delta_f * (cur_delta - delta_0_mt)/(cur_delta * (delta_f - delta_0_mt))
	else:
		dmt = 1
	if ed2 > 1:
		cur_delta = Lc * math.pow(Macaulay(-epsilon_bb)**2 + epsilon_ab**2, 1/2)
		dmc = delta_f * (cur_delta - delta_0_mc)/(cur_delta * (delta_f - delta_0_mc))
	else:
		dmc = 1
	return [dft, dfc, dmt, dmc]

#计算当前复合材料单元的损伤面积
def CalFailedElemArea():
	annotations.DeleteAnnotation(1)
	_, d3plotPath = GUI.GetGeoD3plotPath()
	visibleElems = elements.VisibleElements(0, "MetaPost")
	cur_resultset = results.CurrentResultset(0)
	failure_area = 0
	for e in visibleElems:
		value = ReadWriteTool.ReadScalar(cur_resultset, e)
		if value < 1.0:
			failure_area += e.get_area(cur_resultset)
	failure_area = round(failure_area, 2)
	annotations.CreateEmptyAnnotation("MetaPost", f"该区域损伤面积为：{failure_area}mm"+"\u00b2", 1)

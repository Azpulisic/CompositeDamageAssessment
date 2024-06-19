from meta import *
from os import path

def ReadScalar(resultset, elem):
	return elements.CentroidScalarOfElement(resultset, elem.type, elem.id, elem.second_id).value
	
def GetTanBuMatPara(curModel_id):
	all_materials = materials.Materials(curModel_id)
	for material in all_materials:
		if material.type == 6:
			return {'xc': float(material.get_property('xc')),
					'xt': float(material.get_property('xt')),
					'yc': float(material.get_property('yc')),
					'yt': float(material.get_property('yt')),
					'sc': 79.0,
					'beta': 1.0,
					'alpha': 1,
					'delta_f': 0.02
			}
	
'''
创建一个新的结果集，名称为name,单元集为elems,数据集为data
name:该结果集的名称
elems:数据写入的单元
data:具体数据
'''
def create_resultset(name, elems, data, model_id):
	all_resultsets = results.Resultsets(model_id)
	state_id = len(all_resultsets)
	cycle = 0
	new_result = results.CreateResultset(model_id, state_id, name, cycle)[0]
	new_function_data_name = 'Centroid Scalar Data'
	layer = 'one_value'
	nodal_calc = 'avg'
	region_bounds = 'parts'
	results.StartAddingCentroidScalar(new_result, new_function_data_name, layer, nodal_calc, region_bounds)
	results.AddCentroidScalarOnSomeElements(new_result, elems, data)
	results.EndAddingCentroidScalar(new_result)

#损伤因子数据写入文件
def WriteData(d3plotPath, data, criteria_name):
	file_path  = path.join(path.dirname(d3plotPath), criteria_name + "Data.txt")
	with open(file_path, 'w') as file:
		for i in range(len(data)):
			file.write(','.join(map(str, data[i])) + '\n')

#从文件中读取损伤因子的数据
def ReadData(file_path):
	allData = []
	with open(file_path, 'r') as file:
		for line in file:
			line = line.strip()
			if line:
				allData.append(
					[float(item) if '.' in item else eval(item) for item in line.split(',')])
	return allData

#论文中使用的fun
#创建新的结果集
def CreateFailureRresultset(resultset_name, elements, stiffness_factor_data, model_id):
	final_timestep_id = len(results.Resultsets(model_id))
	stiffness_factor_resultset = results.CreateResultset(model_id, final_timestep_id, resultset_name, 0)[0]
	new_function_data_name = 'stiffness_factor_Data'
	layer = 'one_value'
	nodal_calculate_formulation = 'avg'
	parts = 'parts'
	results.StartAddingCentroidScalar(stiffness_factor_resultset, new_function_data_name, layer, nodal_calculate_formulation, parts)
	results.AddCentroidScalarOnSomeElements(stiffness_factor_resultset, elements, stiffness_factor_data)
	results.EndAddingCentroidScalar(stiffness_factor_resultset)


from meta import *
import GUI

def StartVR():
    #这部分最好先检查VR设备是否连接好了
    vr.Start()

def CloseVR():
    vr.Stop()

def ReadStress():
    curModel_id = 0
    _, d3plotPath = GUI.GetGeoD3plotPath()
    results.LoadScalar(curModel_id, d3plotPath, 'AUTO', 'all', 'Stresses,Normal-1(UCS)')
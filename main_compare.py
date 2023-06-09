
"""
@author: Bahman Ahmadi -- b.ahmadi@utwente.nl
"""
#########################
#__________________________________________-
import sys,os,time,numpy as np,pandas as pd
from datetime import datetime
from PowerSystem.SOL import SOL 
import data.ReadData as RD
PFM=['Alliander']#,'Laurent','tensor','hp','sequential','hp-tensor','fbs','nr','fdxb','gs','dc']
SimTime=[]
for iPFM in PFM:
	Param=SOL()

	FD=os.getcwd()
	sys.path.append(os.path.join(FD,"data"))
	sys.path.append(os.path.join(FD,"PowerSystem"))
	Param.FD=FD


	Param.day=range(1,362)
	Param.TestSystem='Nodes_33'
	Param.TestSystemLines='Lines_33'

	

	Param.PowerFlowMethod=iPFM # 'Alliander','Laurent' or 'tensor', 'hp' , 'sequential' , 'hp-tensor' , "fbs","nr",'fdxb','gs','dc'

	###############################
	if Param.TestSystem=='Nodes_33':
		Param.Sbase = 1000  # kVA
		Param.Vbase = 12.66  # kV
	else:
		print('Test system (S_base and V_base) is not defined!')
	if Param.PowerFlowMethod=='Laurent':
		Param.profile_info=1
		from PowerSystem.pf_functions import makeYbus
		System_Data_Nodes = pd.read_csv(os.path.join(FD,'data/grid_data/'+Param.TestSystem+'.csv'))
		Param.System_Data_Nodes=System_Data_Nodes
		System_Data_Lines = pd.read_csv(os.path.join(FD,'data/grid_data/'+Param.TestSystemLines+'.csv'))
		Yss, Ysd, Yds, Ydd = makeYbus(System_Data_Lines, System_Data_Nodes, Param.Sbase, Param.Vbase)  # Calculates the Ybus submatrices
		Param.Yss=Yss
		Param.Ysd=Ysd
		Param.Yds=Yds
		Param.Ydd=Ydd
	elif Param.PowerFlowMethod in ("fbs","nr",'fdxb','gs','dc'):  #'nr' for Newton-Raphson, 'fdxb' for Fast Decoupled with BX bus splitting, 'gs' for Gauss-Seidel, 'dc' for DC power flow, and 'fbs' for Backward/Forward Sweep
		import pandapower as pp
		from PowerSystem.create_net_data import create_pandapower_net
		Param.profile_info=0
		System_Data_Nodes = pd.read_csv(os.path.join(FD,'data/grid_data/'+Param.TestSystem+'.csv'))
		System_Data_Lines = pd.read_csv(os.path.join(FD,'data/grid_data/'+Param.TestSystemLines+'.csv'))
		Param.network=create_pandapower_net(System_Data_Lines, System_Data_Nodes,Param.Vbase)	
	elif Param.PowerFlowMethod=='Alliander':
		Param.profile_info=0
		from PowerSystem.create_net_data import create_Alliander_net
		System_Data_Nodes = pd.read_csv(os.path.join(FD,'data/grid_data/'+Param.TestSystem+'.csv'))
		System_Data_Lines = pd.read_csv(os.path.join(FD,'data/grid_data/'+Param.TestSystemLines+'.csv'))
		Param.network,Param.sysData=create_Alliander_net(System_Data_Lines, System_Data_Nodes,Param.Vbase)	
	else:
		Param.profile_info=1
		from tensorpowerflow import GridTensor
		Param.network = GridTensor(node_file_path=os.path.join(FD,"data/grid_data/"+Param.TestSystem+".csv"),lines_file_path=os.path.join(FD,"data/grid_data/"+Param.TestSystemLines+".csv"),gpu_mode=False,v_base=Param.Vbase)


	###############################
	#read the time series data
	Read_npy_data='yes'
	tic = time.time()
	if Read_npy_data=='no':
		Param=RD.read_act_react_DATA(Param)
		save_Profiles='yes'
		if save_Profiles=='yes':
			RD.Save_profiles_npy("data/time_series/Profiles_info1",Param)
	else:
		a=Param.day
		Param.day=[1]
		Param=RD.read_act_react_DATA(Param)
		Param.day=a
		if Param.profile_info==0:
			a=np.load('data/time_series/Profiles.npy',allow_pickle=True).item()
		else:
			a=np.load('data/time_series/Profiles_info1.npy',allow_pickle=True).item()
		Param.Profile_actP=a['actPower']
		Param.Profile_actQ=a['reactPower']
	toc=time.time()-tic
	print('Ptorile simtime: ',toc)
	###############################
	folder_name= 'Results'
	from PowerSystem.fobj import fobj
	try:
		os.mkdir(os.path.join(FD,folder_name))
	except:
		pass

	## voltage magnitude resuts for the best solution
	Param.goal='(v-1)^2'
	tic = time.time()
	Param = fobj(Param)
	toc=time.time()-tic
	print('Elapsed time for the power flow: ',toc)
	SimTime.append(toc)
	RD.Save_voltages_npy(os.path.join(FD,folder_name,"Voltages"),Param)
DD = np.array([PFM, SimTime]).T  # Transpose the array to match columns
# Save the data to a CSV file
np.savetxt(os.path.join(FD,folder_name,"SimTimes.csv"), DD, delimiter=',', fmt='%s')
check_pint=1
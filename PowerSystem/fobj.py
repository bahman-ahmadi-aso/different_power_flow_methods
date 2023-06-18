
import numpy as np
import time 
def fobj(Param):

    ## the power flow outs
    if Param.PowerFlowMethod == 'Laurent':
        ########################   Laurent   ############################
        from PowerSystem.pf_functions import run_pf

        nb = Param.System_Data_Nodes.shape[0]
        Vmg = []
        for iSA in range(len(Param.Profile_actP)):
            ViSA=[]
            for iT in range(Param.nTime):
                V_0 = np.ones((nb - 1)) + 1j * np.zeros((nb - 1))  # Flat start
                k = 0
                K = 5  # Max iterations
                tol = 100
                epsilon = 1 * 10 ** (-6)
                PP=np.array(Param.Profile_actP[iSA][iT])
                QQ=np.array(Param.Profile_actQ[iSA][iT])
                while (k <= K) & (tol >= epsilon):
                    V = run_pf(Param.System_Data_Nodes,PP,QQ, Param.Sbase, Param.Yds, Param.Ydd, V_0)
                    tol = max(abs(abs(V) - abs(V_0)))
                    V_0 = V  # Voltage at load buses
                    k += 1
                ViSA.append(abs(V_0))
                Ss = np.conj(Param.Yss + Param.Ysd * V_0)  # Power at substation
            Vmg.append(ViSA)
    elif Param.PowerFlowMethod in ('bfsw',"fbs","nr",'fdxb','gs','dc'):
        import pandapower as pp
        Vmg = []
        for iSA in range(len(Param.Profile_actP)):
            ViSA=[]
            for iT in range(Param.nTime):
                Param.network.load.p_mw=np.array(Param.Profile_actP[iSA][iT])/1000
                Param.network.load.q_mw=np.array(Param.Profile_actQ[iSA][iT])/1000

                pp.runpp(Param.network,algorithm=Param.PowerFlowMethod,init="flat")
                #print(network.res_bus)
                ViSA.append(np.array(Param.network.res_bus.vm_pu))
            Vmg.append(ViSA)
    elif Param.PowerFlowMethod=='Alliander':
        from power_grid_model import LoadGenType
        from power_grid_model import PowerGridModel, CalculationMethod, CalculationType
        from power_grid_model import initialize_array
        Vmg = []
        for iSA in range(len(Param.Profile_actP)):
            load_profile = initialize_array("update", "sym_load", (Param.nTime, Param.nLoad))  
            load_profile["id"] = [Param.sysData["sym_load"]["id"]]

            load_profile["p_specified"] = np.multiply(Param.Profile_actP[iSA],1000)
            load_profile["q_specified"] = np.multiply(Param.Profile_actQ[iSA],1000)

            time_series_mutation = {"sym_load": load_profile}

            output_data = Param.network.calculate_power_flow(
                update_data=time_series_mutation,
                threading=0,
                symmetric=True,
                error_tolerance=1e-8,
                max_iterations=20,
                calculation_method=CalculationMethod.newton_raphson)

            
            #Vm=[[output_data['node'][iT][ibus][2] for ibus in range(Param.nLoad)] for iT in range(Param.nTime)]
            Vmg.append(np.array([[output_data['node'][iT][ibus][2] for ibus in range(Param.nLoad)] for iT in range(Param.nTime)]))

    else: ##tensor 
        if len(Param.Profile_actP)*Param.nTime>960000:
            claster=1000
            uotient, remainder = divmod(len(Param.Profile_actP),claster)
            print(uotient, remainder)
            Vmg=[]
            for i in range(1,uotient+1):
                print(i)
                solutions = Param.network.run_pf(active_power=np.array(Param.Profile_actP[-1+(i*claster-(claster-1)):i*claster-1]),
                        reactive_power=np.array(Param.Profile_actQ[-1+(i*claster-(claster-1)):i*claster-1]),algorithm=Param.PowerFlowMethod)
                Vmg.append(abs(solutions["v"]))
            if remainder>0:
                solutions = Param.network.run_pf(active_power=np.array(Param.Profile_actP[-1+(uotient*claster-(claster-1)):len(Param.Profile_actP)]),
                        reactive_power=np.array(Param.Profile_actQ[-1+(uotient*claster-(claster-1)):len(Param.Profile_actP)]),algorithm=Param.PowerFlowMethod)
                Vmg.append(abs(solutions["v"]))
        else:
            solutions = Param.network.run_pf(active_power=np.array(Param.Profile_actP),
                        reactive_power=np.array(Param.Profile_actQ),algorithm=Param.PowerFlowMethod)
            Vmg=abs(solutions["v"])
    

    ##############################################################
    #calculate the objective value(s)
    fit=[]
    if Param.goal=='(v-1)^2':
        for iSA in range(len(Param.Profile_actP)):
            fit.append(np.sum((Vmg[iSA]-1))**2)
    elif Param.goal=='abs(v-v_ref)':
        for iSA in range(len(Param.Profile_actP)):
            fit.append(np.sum(np.abs(np.add(Vmg[iSA],-1))))
    else:
        fit.append('None')
        print("NO OFs is selected")

    Param.Vmg=Vmg
    Param.goal_value=fit
    return Param


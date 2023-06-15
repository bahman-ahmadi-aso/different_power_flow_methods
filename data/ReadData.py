import os,numpy as np,pandas as pd, matplotlib.pyplot as plt
from datetime import datetime
def read_act_react_DATA(Param):
    for iiday in Param.day:
        ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
        start = '2022-01-01 00:00:00'
        end = '2022-12-31 23:59:00'
        dt = pd.date_range(start=start, end=end)
        dtd = datetime.strptime(str(dt[iiday-1]), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        #load system data
        ##
        df = pd.read_csv(os.path.join(Param.FD,"data/time_series/active_power_scaled_oneyear15min.csv"))
        df['date_time'] = pd.to_datetime(df['date_time'], format="%d/%m/%Y %H:%M")
        date_filter = df['date_time'].dt.date == pd.to_datetime(dtd).date()
        filtered_df = df[date_filter]
        active_power_time_series = filtered_df.iloc[:,1:].values#  1: neglect the first data (column) in csv file
        ##
        df = pd.read_csv(os.path.join(Param.FD,"data/time_series/reactive_power_scaled_oneyear15min.csv"))
        df['date_time'] = pd.to_datetime(df['date_time'], format="%d/%m/%Y %H:%M")
        date_filter = df['date_time'].dt.date == pd.to_datetime(dtd).date()
        filtered_df = df[date_filter]
        reactive_power_time_series =filtered_df.iloc[:,1:].values# 

        LoadData = pd.read_csv(os.path.join(Param.FD,"data/grid_data/"+Param.TestSystem+".csv"),index_col=0,parse_dates=True)
        maxP=LoadData["PD"].values
        maxQ=LoadData["QD"].values
        SameLoadCurve="yes"
        Base_load_data="yes"
        if SameLoadCurve=="yes":
            ap=np.array([[active_power_time_series[t][0] for n in range(len(maxP))] for t in range(len(active_power_time_series))])
            aq=np.array([[reactive_power_time_series[t][0] for n in range(len(maxP))] for t in range(len(active_power_time_series))])
            P_profiles1=maxP*ap
            Q_profiles1=maxQ*aq
            if Base_load_data=="yes":
                scale=np.array([active_power_time_series[t][0] for t in range(len(active_power_time_series))])
                scale=scale/np.max(scale)
                scaleAll1='yes'
                if scaleAll1=='yes':
                    scale=np.add(np.multiply(scale,0),1)
                ap=np.array([[scale[t] for n in range(len(maxP))] for t in range(len(active_power_time_series))])
                aq=np.array([[scale[t] for n in range(len(maxP))] for t in range(len(active_power_time_series))])
                P_profiles1=maxP*ap
                Q_profiles1=maxQ*aq
            Param.P_profiles=P_profiles1
            Param.Q_profiles=Q_profiles1
        else:
            P_profiles1=maxP*active_power_time_series
            Q_profiles1=maxQ*reactive_power_time_series
            Param.P_profiles=P_profiles1
            Param.Q_profiles=Q_profiles1



        withDG='no'
        if withDG=='yes':
            #PV--WT
            ##
            df1 = pd.read_csv(os.path.join(Param.FD,"data/time_series/photovoltaic_oneyear15min.csv"))
            df1['date_time'] = pd.to_datetime(df1['date_time'], format="%d/%m/%Y %H:%M")
            date_filter = df1['date_time'].dt.date == pd.to_datetime(dtd).date()
            filtered_df = df1[date_filter]
            #filtered_df.to_csv('data/time_series/test.csv', index=False)
            PV1 = filtered_df.iloc[:,1:].values#pd.read_csv("data/time_series/test.csv",index_col=0,parse_dates=True).values.tolist()
            Param.PV=[PV1[t][0] for t in range(len(PV1))]
            ##
            df = pd.read_csv(os.path.join(Param.FD,"data/time_series/windturbine_oneyear15min.csv"))
            df['date_time'] = pd.to_datetime(df['date_time'], format="%d/%m/%Y %H:%M")
            date_filter = df['date_time'].dt.date == pd.to_datetime(dtd).date()
            filtered_df = df[date_filter]
            #filtered_df.to_csv('data/time_series/test.csv', index=False)
            WT1 = filtered_df.iloc[:,1:].values#pd.read_csv("data/time_series/test.csv",index_col=0,parse_dates=True).values
            Param.WT=[WT1[t][0] for t in range(len(WT1))]

            pos1=[50,50,50,50,10,50,50,50,50,50,50,10,10,50,50,50,50,50,50,50,50,50,50,50,50,50,10,50,50,50,50,50,50]
            pos2=[-10,-10,-10,-10,10,10,-10,-10,-10,-10,-10,10,-10,-10,10,-10,-10,-10,-10,10,-10,-10,10,-10,-10,-10,10,-10,-10,-10,-10,-10,10]
            pos3=[0,191.959054,281.627274,220.923238,60.198232,102.919964,673.300054,540.673467,208.015236,192.459048,226.313184,75.479149,186.143775,404.096319,86.982228,223.934086,191.888023,275.075937,225.072578,87.124146,355.009229,266.678967,323.513742,999.988744,999.557998,214.221004,132.327062,299.37552,506.294196,701.112671,540.785227,802.466689,189.606793]
            pos3=np.add(pos3,-80)
            pos3[0]=0
            pos=np.append(np.append(pos1,pos2),pos3).tolist()
            Profile_actP=[]  
            DG = []
            Gen=[]
            for iT in range(len(Param.WT)):
                DGtemp=[]
                Gentemp=[]
                for iP in range(len(Param.P_profiles[0])):
                    if pos[iP]>0:
                        if pos[iP+len(Param.P_profiles[0])]>0:  #PV
                            DGtemp.append(np.multiply(Param.PV[iT],pos[iP+2*len(Param.P_profiles[0])]))
                        else:
                            DGtemp.append(np.multiply(Param.WT[iT],pos[iP+2*len(Param.P_profiles[0])]))
                    else:
                        DGtemp.append(0)
                    Gentemp.append(0)
                Gen.append(Gentemp)
                DG.append(DGtemp)
            Profile_actP.append(np.add(np.add(Param.P_profiles,np.multiply(-1,DG)),Gen))
            Param.P_profiles=Profile_actP[0]
            
        Param.P_profiles=Param.P_profiles[:,Param.profile_info:]
        Param.Q_profiles=Param.Q_profiles[:,Param.profile_info:]
        Param.nTime=len(Param.P_profiles)
        Param.nLoad=len(Param.P_profiles[0])
        Param.Profile_actP.append(Param.P_profiles)
        Param.Profile_actQ.append(Param.Q_profiles)
        
        
    return Param

def Save_profiles_npy(name,Param):
    PARAM={'actPower':Param.Profile_actP,
                'reactPower':Param.Profile_actQ}
    np.save(name+'.npy', PARAM)

def Save_voltages_npy(name,Param):
    PARAM={'goal_values':Param.goal_value,'Vmg':Param.Vmg}
    np.save(name+'.npy', PARAM)


def Plot_bars(name,Param,PFM, SimTime,VOF):
    x = np.arange(len(PFM))

    fig, ax = plt.subplots()
    # Create the bars for SimTime
    ax.barh(x, SimTime, color='blue', label='SimTime')
    # Create the bars for VOF
    ax.barh(x, -np.array(VOF), color='red', label='VOF')

    # Set the y-axis tick positions and labels
    ax.set_yticks(x)
    ax.set_yticklabels(PFM)

    # Set the x-axis label
    ax.set_xlabel('Time                            Value')
    max=np.max([np.max(SimTime),np.max(VOF)])
    max=max*1.1
    max2=max*0.15
    ax.set_xlim([-max,max ])
    ax.axis('off')
    # Write the rounded values in front of the bars
    for i, (time, vof) in enumerate(zip(SimTime, VOF)):
        ax.text(time+max2, i, f'{round(time, 4)}', ha='left', va='center', color='black')
        ax.text(-vof-max2, i, f'{round(vof, 4)}', ha='right', va='center', color='black')
        ax.text(0, i, f'{PFM[i]}', ha='right', va='center', color='black')
    
    ax.text(0, -1, r'$\sum|v_{ij}-1|$                            Time (s)', ha='center', va='center', color='black')
    
    # Show Plot
    plt.savefig(name+'.png', bbox_inches='tight')
    a=1



def Plot_bars1(name,Param,PFM, SimTime,VOF):
    # Figure Size
    fig, ax = plt.subplots(figsize =(6, 6))
    
    # Horizontal Bar Plot
    ax.barh(PFM, SimTime)
    
    # Remove axes splines
    for s in ['top', 'bottom', 'left', 'right']:
        ax.spines[s].set_visible(False)
    
    # Remove x, y Ticks
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')
    
    # Add padding between axes and labels
    ax.xaxis.set_tick_params(pad = 5)
    ax.yaxis.set_tick_params(pad = 10)
    
    
    # Show top values
    ax.invert_yaxis()
    
    # Add annotation to bars
    for i in ax.patches:
        plt.text(i.get_width()+0.2, i.get_y()+0.5,
                str(round((i.get_width()), 4)),
                fontsize = 12, fontweight ='bold',
                color ='grey')
    
    
    plt.yticks(fontsize=12)
    # Show Plot
    plt.savefig(name+'.png', bbox_inches='tight')
    a=1






class SOL:
    def __init__(self):
        self.day=[1]


        self.TestSystem='Nodes_33'
        self.TestSystemLines='Lines_33'
        
        self.P_profiles=[]
        self.Q_profiles=[]
        self.profile_info=0
        self.Profile_actP=[]
        self.Profile_actQ=[]

        self.PV=0
        self.WT=0
        self.network=[]
        self.sysData=[]
        self.Yss=[]
        self.Ysd=[]
        self.Yds=[]
        self.Ydd=[]
        self.System_Data_Nodes=0
        self.PowerFlowMethod=0
        self.Vbase=0
        self.Sbase=0


        self.ActProfile=[]
        self.ReactProfile=[]
        self.alphaAct=[]
        self.alphaReact=[]


        self.Directory_name=[]

        self.nTime=0
        self.nLoad=0

        self.goal_value=[]

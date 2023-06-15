



import pandapower.networks as pn
import pandapower as pp
import numpy as np
net = pn.create_dickert_lv_network(feeders_range='long', linetype='cable', customer='multiple', case='bad', trafo_type_name='0.4 MVA 20/0.4 kV', trafo_type_data=None)


pp.runpp(net)

Vmg=net.res_bus.vm_pu







NODES=net.bus.index.values
Tb=net.bus.in_service
Tb=Tb.astype(int)-1
Tb=Tb.values
Tb[0]=1
PD=net.load.p_mw.values
QD=net.load.q_mvar.values

import pandas as pd

# Assuming you have the arrays: NODES, Tb, PD, QD
pdd=[0,0]
qdd=[0,0]
for i in range(len(PD)):
    pdd.append(PD[i]*1000)
    qdd.append(QD[i]*1000)

data = {
    'NODES': NODES,
    'Tb': Tb,
    'PD': pdd,
    'QD': qdd
}

df = pd.DataFrame(data)
df.to_csv('Nodes_150.csv', index=False)


FROM=net.line.from_bus
TO=net.line.to_bus
R=net.line.r_ohm_per_km
X=net.line.x_ohm_per_km
length=net.line.length_km
R=R*length
X=X*length
B=net.line.c_nf_per_km
B=B*length
STATUS=net.line.in_service


data = {
    'FROM': FROM,
    'TO': TO,   
    'R': R,
    'X': X,
    'B': B,
    'STATUS': STATUS.astype(int)
}

df = pd.DataFrame(data)
df.to_csv('Lines_150.csv', index=False)

#np.savetxt("Lines_150.csv", np.transpose([FROM,TO,R,X,B,STATUS]), delimiter=",", fmt='%s')

Vbase=net.bus.vn_kv
Vbase=Vbase[0]










import doGIT
doGIT.doGIT("")

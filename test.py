



import pandapower.networks as pn
import pandapower as pp
import numpy as np
net = pn.create_dickert_lv_network(feeders_range='long', linetype='cable', customer='multiple', case='bad', trafo_type_name='0.4 MVA 20/0.4 kV', trafo_type_data=None)


pp.runpp(net)

NODES=net.bus.index.values
Tb=net.bus.in_service
Tb=Tb.astype(int)-1
Tb=Tb.values
Tb[0]=1
PD=net.load.p_mw.values
QD=net.load.q_mvar.values
np.savetxt("Nodes_150.csv", ([NODES,Tb,PD,QD]), delimiter=",", fmt='%s')


FROM=net.line.from_bus
TO=net.line.to_bus
R=net.line.r_ohm_per_km
X=net.line.x_ohm_per_km
B=net.line.c_nf_per_km
STATUS=net.line.in_service
#np.savetxt("Lines_150.csv", np.transpose([FROM,TO,R,X,B,STATUS]), delimiter=",", fmt='%s')

Vbase=net.bus.vn_kv
Vbase=Vbase[0]










import doGIT
doGIT.doGIT("")

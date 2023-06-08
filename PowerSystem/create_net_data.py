import numpy as np
import pandas as pd
def create_pandapower_net(branch_info_: pd.DataFrame, bus_info_: pd.DataFrame,Vbase):
    import pandapower as pp
    branch_info = branch_info_.copy()
    bus_info = bus_info_.copy()

    net = pp.create_empty_network()
    # Add buses
    bus_dict = {}
    for i, (idx, bus_name) in enumerate(bus_info["NODES"].items()):
        bus_dict[bus_name] = pp.create_bus(net, vn_kv=Vbase, name=f"Bus {bus_name}")

    # Slack
    bus_slack = bus_info[bus_info["Tb"] == 1]["NODES"].values
    assert len(bus_slack.shape) == 1 and bus_slack.shape[0] == 1, "Only one slack bus supported"
    pp.create_ext_grid(net, bus=bus_dict[bus_slack.item()], vm_pu=1.00, name="Grid Connection")

    # Lines
    for i, (idx, (from_bus, to_bus, res, x_react, b_susceptance)) in enumerate(
    branch_info[["FROM", "TO", "R", "X", "B"]].iterrows()):
        pp.create_line_from_parameters(net,
        from_bus=bus_dict[from_bus], to_bus=bus_dict[to_bus],
        length_km=1, r_ohm_per_km=res, x_ohm_per_km=x_react, c_nf_per_km=b_susceptance,
        max_i_ka=10, name=f"Line {i + 1}")

    # Loads:
    for i, (idx, (node, p_kw, q_kvar)) in enumerate(bus_info[["NODES", "PD", "QD"]].iterrows()):
        pp.create_load(net, bus=bus_dict[node], p_mw=p_kw / 1000., q_mvar=q_kvar / 1000., name=f"Load")

    return net


def create_Alliander_net(branch_info_: pd.DataFrame, bus_info_: pd.DataFrame,Vbase):
    from power_grid_model import LoadGenType
    from power_grid_model import PowerGridModel, CalculationMethod
    from power_grid_model import initialize_array
    # node
    node = initialize_array("input", "node", len(bus_info_))
    node["id"] = np.array([i+1 for i in range(len(bus_info_))])
    node["u_rated"] = [Vbase*1000 for i in range(len(bus_info_))]

    # line
    line = initialize_array("input", "line", len(branch_info_))
    line["id"] = [i+len(node["id"])+1 for i in range(len(branch_info_))]
    line["from_node"] = branch_info_['FROM']
    line["to_node"] = branch_info_['TO']
    line["from_status"] = [1 for i in range(len(branch_info_))]
    line["to_status"] = [1 for i in range(len(branch_info_))]
    line["r1"] = branch_info_['R']
    line["x1"] = branch_info_['X']
    line["c1"] = branch_info_['B']
    line["tan1"] = [0.0 for i in range(len(branch_info_))]
    line["i_n"] = [1000 for i in range(len(branch_info_))]

    # load
    sym_load = initialize_array("input", "sym_load", len(bus_info_))
    sym_load["id"] = [i+len(node["id"])+len(line["id"])+1 for i in range(len(bus_info_))]
    sym_load["node"] = [i+1 for i in range(len(bus_info_))]
    sym_load["status"] = [1 for i in range(len(bus_info_))]
    sym_load["type"] = [LoadGenType.const_power for i in range(len(bus_info_))]
    sym_load["p_specified"] = np.multiply(bus_info_['PD'],1000)
    sym_load["q_specified"] = np.multiply(bus_info_['QD'],1000)

    # source
    source = initialize_array("input", "source", len([i+1 for i in range(len(bus_info_)) if bus_info_["Tb"][i]==1]))
    source["id"] = [i+len(node["id"])+len(line["id"])+len(sym_load["id"])+1 for i in range(len([i+1 for i in range(len(bus_info_)) if bus_info_["Tb"][i]==1]))]
    source["node"] = [i+1 for i in range(len(bus_info_)) if bus_info_["Tb"][i]==1]
    source["status"] = [1 for i in range(len(bus_info_)) if bus_info_["Tb"][i]==1]
    source["u_ref"] = [1.0 for i in range(len(bus_info_)) if bus_info_["Tb"][i]==1]

    input_data = {
    "node": node,
    "line": line,
    "sym_load": sym_load,
    "source": source}

    model = PowerGridModel(input_data)
    testmethod='no' #need to be corrected
    if testmethod=='yes':
        output_data = model.calculate_power_flow(
        #update_data=time_series_mutation,
        threading=0,
        symmetric=True,
        error_tolerance=1e-8,
        max_iterations=20,
        calculation_method=CalculationMethod.newton_raphson)

        n_BUS=33
        n_Time=1
        Vm=[[output_data['node'][iT][ibus][2] for ibus in range(n_BUS)] for iT in range(n_Time)]

    net=1
    return model,input_data
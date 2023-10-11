import gurobipy as gp

def get_opt_result(P_D_load, GHR_load, E_P_load, ES, PV, T_num, ES_IC, PV_IC, data_id):
    total = P_D_load[data_id, :, :].reshape(-1)
    GHR = GHR_load[data_id, :, :].reshape(-1)
    electricity_price = E_P_load[data_id, :, :].reshape(-1)
    M = 10000

    model = gp.Model()
    ES_install = model.addMVar((ES.types_num, 1), lb=ES.min_invest,
                               ub=ES.max_invest, vtype=gp.GRB.CONTINUOUS)
    PC = model.addMVar((ES.types_num, T_num), lb=0, vtype=gp.GRB.CONTINUOUS)
    PD = model.addMVar((ES.types_num, T_num), lb=0, vtype=gp.GRB.CONTINUOUS)
    # 目标函数：收益最大
    model.setObjective(gp.quicksum(ES.invest_cost[i] * ES_install[i, 0] for i in range(ES.types_num)) +
                       gp.quicksum(gp.quicksum(PC[i, t] - PD[i, t] for i in range(ES.types_num))
                                   * 0.25 * electricity_price[t] for t in range(T_num)), gp.GRB.MINIMIZE)

    # 约束条件：不过放
    model.addConstrs(gp.quicksum(PD[i, t] - PC[i, t] for i in range(ES.types_num)) <= total[t] for t in range(T_num))
    # 约束条件：储能约束
    model.addConstrs(PC[:, t] <= ES.maxPC * ES_install[:, 0] for t in range(T_num))
    model.addConstrs(PD[:, t] <= ES.maxPD * ES_install[:, 0] for t in range(T_num))
    for i in range(ES.types_num):
        for t in range(1, T_num + 1):
            model.addConstr(ES.maxE[i] * ES_install[i, 0] >= gp.quicksum(PC[i, tt] - PD[i, tt] for tt in range(t))
                            + ES.maxE0[i] * ES_install[i, 0])
            model.addConstr(0 <= gp.quicksum(PC[i, tt] - PD[i, tt] for tt in range(t)) +
                            ES.maxE0[i] * ES_install[i, 0])
        model.addConstr(0 == gp.quicksum(PC[i, tt] - PD[i, tt] for tt in range(T_num)))
    model.setParam('OutputFlag', 0)
    model.optimize()
    obj_onlyES = model.objVal
    del model

    model = gp.Model()
    PV_install = model.addMVar((PV.types_num, 1), lb=PV.min_invest,
                               ub=PV.max_invest, vtype=gp.GRB.CONTINUOUS)
    PPV = model.addMVar((PV.types_num, T_num), lb=0, vtype=gp.GRB.CONTINUOUS)
    # 目标函数：收益最大
    model.setObjective(gp.quicksum(PV.invest_cost[i] * PV_install[i, 0] for i in range(PV.types_num)) -
                       gp.quicksum(gp.quicksum(PPV[i, t] for i in range(PV.types_num))
                                   * 0.25 * electricity_price[t] for t in range(T_num)), gp.GRB.MINIMIZE)
    # 约束条件：光伏出力约束
    model.addConstrs(PPV[:, t] <= GHR[t] * PV.area * PV_install[:, 0] * PV.yita for t in range(T_num))
    model.addConstrs(gp.quicksum(PPV[i, t] for i in range(PV.types_num)) <= total[t] for t in range(T_num))
    model.setParam('OutputFlag', 0)
    model.optimize()
    obj_onlyPV = model.objVal
    del model

    model = gp.Model()
    ES_install = model.addMVar((ES.types_num, 1), lb=ES.min_invest,
                               ub=ES.max_invest, vtype=gp.GRB.CONTINUOUS)
    PV_install = model.addMVar((PV.types_num, 1), lb=PV.min_invest,
                               ub=PV.max_invest, vtype=gp.GRB.CONTINUOUS)
    PC = model.addMVar((ES.types_num, T_num), lb=0, vtype=gp.GRB.CONTINUOUS)
    PD = model.addMVar((ES.types_num, T_num), lb=0, vtype=gp.GRB.CONTINUOUS)
    PPV = model.addMVar((PV.types_num, T_num), lb=0, vtype=gp.GRB.CONTINUOUS)
    # 目标函数：收益最大
    model.setObjective(gp.quicksum(ES.invest_cost[i] * ES_install[i, 0] for i in range(ES.types_num)) +
                       gp.quicksum(PV.invest_cost[i] * PV_install[i, 0] for i in range(PV.types_num)) +
                       gp.quicksum(gp.quicksum(PC[i, t] - PD[i, t] for i in range(ES.types_num))
                                   * 0.25 * electricity_price[t] for t in range(T_num)) -
                       gp.quicksum(gp.quicksum(PPV[i, t] for i in range(PV.types_num))
                                   * 0.25 * electricity_price[t] for t in range(T_num)), gp.GRB.MINIMIZE)
    # 约束条件1：光伏出力约束
    model.addConstrs(PPV[:, t] <= GHR[t] * PV.area * PV_install[:, 0] * PV.yita for t in range(T_num))
    # 约束条件2：不过放
    model.addConstrs(gp.quicksum(PPV[i, t] for i in range(PV.types_num)) +
                     gp.quicksum(PD[i, t] - PC[i, t] for i in range(ES.types_num)) <= total[t] for t in range(T_num))
    # 约束条件3：储能约束
    model.addConstrs(PC[:, t] <= ES.maxPC * ES_install[:, 0] for t in range(T_num))
    model.addConstrs(PD[:, t] <= ES.maxPD * ES_install[:, 0] for t in range(T_num))
    for i in range(ES.types_num):
        for t in range(1, T_num + 1):
            model.addConstr(ES.maxE[i] * ES_install[i, 0] >= gp.quicksum(PC[i, tt] - PD[i, tt] for tt in range(t))
                            + ES.maxE0[i] * ES_install[i, 0])
            model.addConstr(0 <= gp.quicksum(PC[i, tt] - PD[i, tt] for tt in range(t)) +
                            ES.maxE0[i] * ES_install[i, 0])
        model.addConstr(0 == gp.quicksum(PC[i, tt] - PD[i, tt] for tt in range(T_num)))
    model.setParam('OutputFlag', 0)
    model.optimize()
    obj_ESPV = 1.0 * model.objVal
    del model

    model = gp.Model()
    ES_install = model.addMVar((ES.types_num, 1), lb=0, ub=ES.max_invest, vtype=gp.GRB.CONTINUOUS)
    PV_install = model.addMVar((PV.types_num, 1), lb=0, ub=PV.max_invest, vtype=gp.GRB.CONTINUOUS)
    ES_judge = model.addMVar((ES.types_num, 1), lb=0, vtype=gp.GRB.BINARY)
    PV_judge = model.addMVar((PV.types_num, 1), lb=0, vtype=gp.GRB.BINARY)
    PC = model.addMVar((ES.types_num, T_num), lb=0, vtype=gp.GRB.CONTINUOUS)
    PD = model.addMVar((ES.types_num, T_num), lb=0, vtype=gp.GRB.CONTINUOUS)
    PPV = model.addMVar((PV.types_num, T_num), lb=0, vtype=gp.GRB.CONTINUOUS)
    # 目标函数：收益最大
    model.setObjective(gp.quicksum(ES_IC[data_id] * ES.invest_cost[i] * ES_install[i, 0] for i in range(ES.types_num)) +
                       gp.quicksum(PV_IC[data_id] * PV.invest_cost[i] * PV_install[i, 0] for i in range(PV.types_num)) +
                       gp.quicksum(gp.quicksum(PC[i, t] - PD[i, t] for i in range(ES.types_num))
                                   * 0.25 * electricity_price[t] for t in range(T_num)) -
                       gp.quicksum(gp.quicksum(PPV[i, t] for i in range(PV.types_num))
                                   * 0.25 * electricity_price[t] for t in range(T_num)), gp.GRB.MINIMIZE)
    # 约束条件1：光伏出力约束
    model.addConstrs(PPV[:, t] <= GHR[t] * PV.area * PV_install[:, 0] * PV.yita for t in range(T_num))
    model.addConstr(PV_judge[:, 0] * PV.min_invest <= PV_install[:, 0])
    model.addConstr(PV_judge[:, 0] * M >= PV_install[:, 0])
    # 约束条件2：不过放
    model.addConstrs(gp.quicksum(PPV[i, t] for i in range(PV.types_num)) +
                     gp.quicksum(PD[i, t] - PC[i, t] for i in range(ES.types_num)) <= total[t] for t in range(T_num))
    # 约束条件3：储能约束
    model.addConstrs(PC[:, t] <= ES.maxPC * ES_install[:, 0] for t in range(T_num))
    model.addConstrs(PD[:, t] <= ES.maxPD * ES_install[:, 0] for t in range(T_num))
    model.addConstr(ES_judge[:, 0] * ES.min_invest <= ES_install[:, 0])
    model.addConstr(ES_judge[:, 0] * M >= ES_install[:, 0])
    for i in range(ES.types_num):
        for t in range(1, T_num + 1):
            model.addConstr(ES.maxE[i] * ES_install[i, 0] >= gp.quicksum(PC[i, tt] - PD[i, tt] for tt in range(t))
                            + ES.maxE0[i] * ES_install[i, 0])
            model.addConstr(0 <= gp.quicksum(PC[i, tt] - PD[i, tt] for tt in range(t)) +
                            ES.maxE0[i] * ES_install[i, 0])
        model.addConstr(0 == gp.quicksum(PC[i, tt] - PD[i, tt] for tt in range(T_num)))
    model.setParam('OutputFlag', 0)
    model.setParam('MIPGap', 0.0)
    model.optimize()
    ES_install01_load = ES_judge.x.reshape(-1)
    PV_install01_load= PV_judge.x.reshape(-1)
    del model

    model = gp.Model()
    ES_install = model.addMVar((ES.types_num, 1), lb=0, ub=ES.max_invest, vtype=gp.GRB.CONTINUOUS)
    PV_install = model.addMVar((PV.types_num, 1), lb=0, ub=PV.max_invest, vtype=gp.GRB.CONTINUOUS)
    PC = model.addMVar((ES.types_num, T_num), lb=0, vtype=gp.GRB.CONTINUOUS)
    PD = model.addMVar((ES.types_num, T_num), lb=0, vtype=gp.GRB.CONTINUOUS)
    PPV = model.addMVar((PV.types_num, T_num), lb=0, vtype=gp.GRB.CONTINUOUS)
    # 目标函数：收益最大
    model.setObjective(gp.quicksum(ES_IC[data_id] * ES.invest_cost[i] * ES_install[i, 0] for i in range(ES.types_num)) +
                       gp.quicksum(PV_IC[data_id] * PV.invest_cost[i] * PV_install[i, 0] for i in range(PV.types_num)) +
                       gp.quicksum(gp.quicksum(PC[i, t] - PD[i, t] for i in range(ES.types_num))
                                   * 0.25 * electricity_price[t] for t in range(T_num)) -
                       gp.quicksum(gp.quicksum(PPV[i, t] for i in range(PV.types_num))
                                   * 0.25 * electricity_price[t] for t in range(T_num)), gp.GRB.MINIMIZE)
    # 约束条件1：光伏出力约束
    model.addConstrs(PPV[:, t] <= GHR[t] * PV.area * PV_install[:, 0] * PV.yita for t in range(T_num))
    # 约束条件2：不过放
    model.addConstrs(gp.quicksum(PPV[i, t] for i in range(PV.types_num)) +
                     gp.quicksum(PD[i, t] - PC[i, t] for i in range(ES.types_num)) <= total[t] for t in range(T_num))
    # 约束条件3：储能约束
    model.addConstrs(PC[:, t] <= ES.maxPC * ES_install[:, 0] for t in range(T_num))
    model.addConstrs(PD[:, t] <= ES.maxPD * ES_install[:, 0] for t in range(T_num))
    for i in range(ES.types_num):
        for t in range(1, T_num + 1):
            model.addConstr(ES.maxE[i] * ES_install[i, 0] >= gp.quicksum(PC[i, tt] - PD[i, tt] for tt in range(t))
                            + ES.maxE0[i] * ES_install[i, 0])
            model.addConstr(0 <= gp.quicksum(PC[i, tt] - PD[i, tt] for tt in range(t)) +
                            ES.maxE0[i] * ES_install[i, 0])
        model.addConstr(0 == gp.quicksum(PC[i, tt] - PD[i, tt] for tt in range(T_num)))
    model.setParam('OutputFlag', 0)
    model.setParam('MIPGap', 0.0)
    model.optimize()

    ES_install_load = ES_install.x.reshape(-1)
    PV_install_load = PV_install.x.reshape(-1)

    return ES_install_load, PV_install_load, ES_install01_load, PV_install01_load, obj_onlyES, obj_onlyPV, obj_ESPV
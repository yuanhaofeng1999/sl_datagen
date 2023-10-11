import numpy as np
from investment_item import ES, PV
import multiprocessing as mp
from get_opt_result import get_opt_result

P_D_load = np.load('P_D.npy')
E_P_load = np.load('E_P.npy')
GHR_load = np.load('GHR.npy')

ES_IC = np.load('ES_IC.npy')
PV_IC = np.load('PV_IC.npy')

ES_install_load = np.zeros((P_D_load.shape[0], 1))
PV_install_load = np.zeros((P_D_load.shape[0], 1))
ES_install01_load = np.zeros((P_D_load.shape[0], 1))
PV_install01_load = np.zeros((P_D_load.shape[0], 1))
cost_save_onlyES_load = np.zeros(P_D_load.shape[0])
cost_save_onlyPV_load = np.zeros(P_D_load.shape[0])
cost_save_ESPV_load = np.zeros(P_D_load.shape[0])

ES = ES()
PV = PV()
T_num = 96

if __name__ == '__main__':
    num_each_par = 10
    for par_round in range(0, P_D_load.shape[0], num_each_par):
        print(par_round)
        opt_result = []
        pool = mp.Pool(processes=num_each_par)
        for data_id in range(par_round, np.min((par_round+num_each_par, P_D_load.shape[0]))):
            opt_result.append(pool.apply_async(get_opt_result, args=(P_D_load, GHR_load, E_P_load, ES, PV, T_num,
                                                                      ES_IC, PV_IC, data_id)))
        pool.close()
        pool.join()

        ES_install_load[par_round:np.min((par_round+num_each_par, P_D_load.shape[0])),:] = \
            np.array([result.get()[0] for result in opt_result])
        PV_install_load[par_round:np.min((par_round+num_each_par, P_D_load.shape[0])),:] = \
            np.array([result.get()[1] for result in opt_result])
        ES_install01_load[par_round:np.min((par_round+num_each_par, P_D_load.shape[0])),:] = \
            np.array([result.get()[2] for result in opt_result])
        PV_install01_load[par_round:np.min((par_round+num_each_par, P_D_load.shape[0])),:] = \
            np.array([result.get()[3] for result in opt_result])
        cost_save_onlyES_load[par_round:np.min((par_round+num_each_par, P_D_load.shape[0]))] = \
            np.array([result.get()[4] for result in opt_result])
        cost_save_onlyPV_load[par_round:np.min((par_round+num_each_par, P_D_load.shape[0]))] = \
            np.array([result.get()[5] for result in opt_result])
        cost_save_ESPV_load[par_round:np.min((par_round+num_each_par, P_D_load.shape[0]))] = \
            np.array([result.get()[6] for result in opt_result])

        if (par_round + 1) % 500 == 0:
            np.save('ES_install.npy', ES_install_load)
            np.save('PV_install.npy', PV_install_load)
            np.save('ES_install01.npy', ES_install01_load)
            np.save('PV_install01.npy', PV_install01_load)

            '''
            np.save('cost_save_onlyES.npy', cost_save_onlyES_load)
            np.save('cost_save_onlyPV.npy', cost_save_onlyPV_load)
            np.save('cost_save_ESPV.npy', cost_save_ESPV_load)
            '''
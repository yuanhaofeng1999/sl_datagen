import numpy as np

class ES:
    def __init__(self):
        # 种类数量
        self.types_num = 1
        # 投资成本
        self.invest_cost = np.array([0.78])
        # 储能最大存储能量
        self.maxE = np.array([2])
        # 储能初始存储能量
        self.maxE0 = np.array([1])
        # 储能最大充电功率
        self.maxPC = np.array([1])
        # 储能最大放电功率
        self.maxPD = np.array([1])
        # 储能起装量
        self.min_invest = np.array([3])
        self.max_invest = np.array([45])

class PV:
    def __init__(self):
        # 种类数量
        self.types_num = 1
        # 投资成本
        self.invest_cost = np.array([0.68])
        # 每kw光伏所占面积m2
        self.area = np.array([6.25])
        # 光伏效率
        self.yita = np.array([0.2])
        self.min_invest = np.array([3])
        self.max_invest = np.array([45])
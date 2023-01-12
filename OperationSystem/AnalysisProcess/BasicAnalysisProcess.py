import os
from abc import abstractmethod
import numpy as np
import pandas as pd
from loguru import logger
from tqdm import tqdm



class BasicAnalysisProcess:
    def __init__(self) -> None:
        pass


    @abstractmethod
    def initial(self, controller=None, config=None, streaming=None, messenger=None):

        # 3 essentials: controller, config, and data streaming client
        self.controller = controller
        self.config = config
        self.streaming = streaming
        self.messenger = messenger
        self.logger = logger

        # 初始化算法：fbcca
        self.targetNUM = config.targetNUM
        # 训练 trial 数目
        self.trainNUM = config.trainBlockNUM * config.targetNUM
        # 测试 trial 数目
        self.testNUM = config.testBlockNUM * config.targetNUM
        self.winLEN = config.winLEN
        self.srate = config.srate
        self.personName = config.personName
        self.paradigm = config.paradigm
        self.prepareFolder()

        self.displayChar = config.displayChar
        self.cueEvents = config.cueEvents
        self.lag = config.lag
        self.n_band = config.n_band

    def prepareFolder(self):
        fatherAdd = 'OperationSystem/ResultStored'
        sonAdd = os.path.join(fatherAdd,self.personName)
        if not os.path.exists(sonAdd):
            os.makedirs(os.path.join(sonAdd, 'images'))
            os.makedirs(os.path.join(sonAdd, 'models'))
            os.makedirs(os.path.join(sonAdd, 'data'))
            os.makedirs(os.path.join(sonAdd, 'record'))
            os.makedirs(os.path.join(sonAdd, 'stimulus'))
        self.savepath = sonAdd
        return


    @abstractmethod
    def run(self):

        pass


    @abstractmethod
    def getResult(self,data):
        result = self.algorithm.predict(data)
        return result[0]


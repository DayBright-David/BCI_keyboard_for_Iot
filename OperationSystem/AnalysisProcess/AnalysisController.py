from OperationSystem.AnalysisProcess.TestingProcess import TestingProcess
from OperationSystem.AnalysisProcess.WaitAnalysisProcess import WaitAnalysisProcess
from OperationSystem.AnalysisProcess.TrainingProcess import TrainingProcess
import pandas as pd
import pickle
import datetime
import os

class AnalysisController:
    def __init__(self):
        self.current_process = None
        self.algorithm = None

        self.currentBlockINX=0
        self.currentEpochINX = 0

        # 等待训练结束后会改变Flag
        self.trainFlag = False

    def initial(self, config, streaming,messenger):

        self.messenger = messenger

        # 个人数据
        self.trainData = dict(
            X = [],# data
            y = [], # label
        )
        self.testData = dict(
            X=[],  # data
            y=[],  # label
        )

        self.results = []

        # 训练阶段
        self.training_process = TrainingProcess()
        self.training_process.initial(self, config, streaming, messenger)

        # 测试阶段
        self.testing_process = TestingProcess()
        self.testing_process.initial(self, config, streaming, messenger)

        # 等待下一次处理
        self.wait_process = WaitAnalysisProcess()
        self.wait_process.initial(self, config, streaming, messenger)

        self.current_process = self.wait_process

        return self

    def report(self, resultID):
        message = 'RSLT:'+str(int(resultID))
        self.messenger.send_exchange_message(message)


    def run(self):
        # algorithm需要在各个状态之间传递
        self.current_process.run()





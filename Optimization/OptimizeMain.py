import sys
sys.path.append('.')

from Optimizer import Optimizier
from OperationSystem.Streaming.NeuroScanEEG import NeuroScanEEGThread
from CommonSystem.Config import Config

# 实验参数
config = Config()
config.expINFO(winLEN=0.3,lag=0.14,targetNUM=40,chnNUM=1)
config.connectINFO(streaming_ip='192.168.1.4',streaming_port=4000,host_ip='192.168.1.75')
config.optimizedINFO(optWIN=1,optBlockNUM=4,classNUM=160)

config.personName = input('Enter subject\'s name:')

# 在线数据
dataStreaming = NeuroScanEEGThread(config=config,keepEvent=True)
dataStreaming.connect()

# optimizer
optimizer = Optimizier(config=config, dataStreaming=dataStreaming,tobeOpt=False)

while not optimizer.endFlag:
    optimizer.collectData()

# pick personal optimized codeset
optimizer.optimize()



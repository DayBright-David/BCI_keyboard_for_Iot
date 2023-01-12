import sys
sys.path.append('.')

import time
from CommonSystem.Config import Config
from StimulationSystem.stimulationOperator import stimulationOperator
from StimulationSystem.StimulationProcess.StimulationController import StimulationController 
from CommonSystem.MessageReceiver.ExchangeMessageManagement import ExchangeMessageManagement
from UICreator.UIFactory import UIFactory

# ----
personName = input('Enter your name:')
paradigm = input('Enter paradigm type(wn/ssvep):')


config = Config()
config.subINFO(personName=personName)
config.expINFO(winLEN=0.5,trainBlockNUM=9,testBlockNUM=0,paradigm=paradigm)
config.displayINFO(stiLEN=0.5,paradigm=paradigm)
config.connectINFO(COM='3100')


# config.addSTI = 'StimulationSystem/pics/'+config.paradigm
factory = UIFactory(config)
frames = factory.getFrames()
factory.saveFrames(frames)

 
stimulationOperator = stimulationOperator()

messenager = ExchangeMessageManagement('server',stimulationOperator,config)
messenager.start()


stimulationOperator.messenager = messenager


stimulator = StimulationController().initial(config,messenager)
# stimulation准备好后给op发消息
message = 'STON'
messenager.send_exchange_message(message)

while messenager.state.status != 'TNOK':
    time.sleep(0.1)

while messenager.state.status != 'EXIT':
    stimulator.run()
    time.sleep(0.1)

import sys
sys.path.append('.')

import time
from CommonSystem.Config import Config
from StimulationSystem.stimulationOperator import stimulationOperator
from StimulationSystem.StimulationProcess.StimulationController import StimulationController 
from CommonSystem.MessageReceiver.ExchangeMessageManagement import ExchangeMessageManagement
from UICreator.UIFactory import UIFactory

personName = input('Enter your name:')
paradigm = input('Enter paradigm type(wn/ssvep):')

config = Config()
config.subINFO(personName=personName)
config.expINFO(winLEN=0.3,trainBlockNUM=0,testBlockNUM=5,paradigm=paradigm)
config.displayINFO(stiLEN=0.3,paradigm=paradigm)


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

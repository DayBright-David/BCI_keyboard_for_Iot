import sys

from matplotlib.pyplot import text
sys.path.append('.')

import time
from CommonSystem.Config import Config
from StimulationSystem.stimulationOperator import stimulationOperator
from StimulationSystem.StimulationProcess.StimulationController import StimulationController 
from CommonSystem.MessageReceiver.ExchangeMessageManagement import ExchangeMessageManagement
from UICreator.UIFactory import UIFactory

# ----
config = Config()

texts = [
        'high speed broadband bci',
        'high speed broadband bci',
        'high speed broadband bci',
        'high speed broadband bci'
        ]

personName = 'diode'
paradigm = 'wn'

config = Config()
config.subINFO(personName=personName)
config.expINFO(winLEN=0.3,trainBlockNUM=2,testBlockNUM=0,paradigm=paradigm,texts=texts)
config.displayINFO(stiLEN=0.5,paradigm=paradigm)
config.connectINFO(COM='3EFC')


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

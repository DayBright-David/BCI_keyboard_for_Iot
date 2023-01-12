import sys
sys.path.append('.')

from CommonSystem.Config import Config
from StimulationSystem.UICreator.UIFactory import UIFactory

for paradigm in ['ssvep','wn']:
    config = Config()
    config.stiLEN=1
    config.personName='wn'
    config.paradigm = paradigm

    factory = UIFactory(config)
    frames = factory.getFrames()
    factory.saveFrames(frames)


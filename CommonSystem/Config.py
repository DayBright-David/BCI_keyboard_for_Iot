import numpy as np
import math
import random
import string


class Config():

    def __init__(self) -> None:
        self.defaultConfig()
        pass

    def defaultConfig(self,):

        self.displayINFO()
        self.subINFO()
        self.expINFO()
        self.connectINFO()

        pass

    def subINFO(self, personName='joedoe', age='unknown', gender='m/f'):
        self.personName = personName
        self.age = age
        self.gender = gender
        pass



    def displayINFO(self, refreshRate=60, stiLEN=3, resolution=(1920, 1080), layout=(5, 8), cubicSize=140, interval=50, trim=(225, 90), phase=[i* np.pi for i in [0, 0.35, 0.70, 1.05, 1.40,1.75, 0.1, 0.45, 0.80, 1.15,1.50, 1.85, 0.20, 0.55, 0.9, 1.25, 1.60, 1.95, 0.30, 0.65, 1.0, 1.35, 1.70, 0.05, 0.40, 0.75, 1.10, 1.45, 1.80, 0.15, 0.50, 0.85, 1.20, 1.55, 1.90, 0.25, 0.60, 0.95, 1.30, 1.65]], frequency=np.linspace(8.0, 15.8, 40), char=list(string.ascii_lowercase) + list(np.arange(10))+['.', ' ', ',', '?'],paradigm='wn'):

        self.paradigm  = paradigm
        self.refreshRate = refreshRate
        self.stiLEN = stiLEN

        self.resolution = resolution
        self.layout = layout
        self.cubicSize = cubicSize
        self.interval = interval
        self.trim = trim

        self.frequency = frequency
        self.phase = phase
        # char 需要转换为按照列排列的顺序
        self.char = np.reshape(char,layout[::-1],order='F').flatten().tolist()

        self.addSTI = 'StimulationSystem/pics/'+paradigm
        pass

    def expINFO(self, targetNUM=40, trainBlockNUM=6, testBlockNUM=6, srate=250, winLEN=1,lag=0.14,n_band=5,chnNUM=9, paradigm='ssvep', saveAdd='picFolder', texts='random',ISI=0.5):

        self.paradigm = paradigm
        self.saveAdd = saveAdd
        self.targetNUM = targetNUM
        self.trainBlockNUM = trainBlockNUM
        self.testBlockNUM = testBlockNUM
        self.blockNUM = trainBlockNUM+testBlockNUM
        self.srate = srate
        self.lag = lag
        self.winLEN = winLEN
        self.n_band = n_band
        self.chnNUM = chnNUM
        self.ISI = ISI

        self.projectCue(texts)

        pass

    def connectINFO(self, COM='3100', streaming_ip='192.168.1.13', streaming_port=4455, record_srate=1000, host_ip='192.168.1.3', host_port=11000):

        self.COM = COM
        self.streaming_ip = streaming_ip
        self.streaming_port = streaming_port
        self.record_srate = record_srate

        self.host_ip = host_ip
        self.host_port = host_port

        pass

    def optimizedINFO(self,optWIN=1,optBlockNUM=5,classNUM=160,seedNUM=1000):

        # optWIN>=self.winLEN
        self.optWIN = optWIN
        self.optBlockNUM = optBlockNUM
        self.classNUM = classNUM
        self.seedNUM = seedNUM

        pass

    def projectCue(self, texts):

        if self.paradigm == 'wn':
            self.events = np.arange(1,self.targetNUM+1,1).tolist()
        elif self.paradigm == 'ssvep':
            self.events = np.arange(self.targetNUM+1, 2*self.targetNUM+1, 1).tolist()

        if texts == 'random':

            # random.seed(253)
            # cueIndice = np.arange(0,self.targetNUM,1)
            # cueIndice 是cue的索引
            # random.shuffle(cueIndice)
            # cueIndice = [0,6,12,10,2,5,11,1,7,17,
            #             29,27,19,23,34,37,39,32,38,33,
            #             25,21,28,35,20,22,14,3,18,26,
            #             36,31,30,15,16,13,4,9,24,8]

            cueIndice = [
                0,1,2,3,4,
                9,8,7,6,5,
                10,11,12,13,14,
                19,18,17,16,15,
                20,21,22,23,24,
                29,28,27,26,25,
                30,31,32,33,34,
                39,38,37,36,35,
            ]
            cueEvents = [self.events[i] for i in cueIndice]
            cueChars = ['%s' % self.char[i] for i in cueIndice]

        else:
            cueEvents = [[self.events[self.char.index(s)] for s in text] for text in texts]
            cueIndice = [[self.char.index(s) for s in text] for text in texts]
            cueChars = texts

            # cue 是 cue的标签
        self.cueEvents = np.tile(cueEvents, (self.blockNUM, 1)).tolist()
        self.cueIndices = np.tile(cueIndice, (self.blockNUM, 1)).tolist()
        self.displayChar = np.tile(cueChars, (self.blockNUM, 1)).tolist()

        return


if __name__ == '__main__':

    config = Config()
    texts = ['am i in control? ']

    config.expINFO(trainBlockNUM=1,testBlockNUM=0,texts=texts)

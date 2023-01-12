from StimulationSystem.StimulationProcess.viewContainer import viewContainer
from StimulationSystem.StimulationProcess.PrePareProcess import PrepareProcess
from StimulationSystem.StimulationProcess.StimulateProcess import StimulateProcess
from StimulationSystem.StimulationProcess.FinishProcess import FinishProcess
from StimulationSystem.StimulationProcess.IdleProcess import IdleProcess
from psychopy import visual
from psychopy import core
import os
import pickle
from tqdm import tqdm
import datetime

class StimulationController:
    def __init__(self):
        # 各个状态
        self.initialProcess = None
        self.prepareProcess = None
        self.stimulateProcess = None
        self.idleProcess = None
        self.finishProcess = None
        self.currentProcess = None
        
        # 显示界面
        self.w = None
        
        self.endBlock = False
        self.endSession = None

        # 当前epoch的cue
        self.cueId = None   
        # 当前block的提示编号
        self.blockCues = None
        # 当前block提示字符
        self.blockCueText = None
        # 当前epoch的编号
        self.currentEpochINX = 0
        # 当前block内epoch的编号
        self.epochThisBlock = 0
        # 当前block的编号
        self.currentBlockINX = 0
        # 当前epoch的结果（由operation返回）
        self.currentResult = None
        # 用户打字的字符框反馈
        self.feedback = None
        # 字符映射
        self.end = False
        


    def initial(self, config, messenager):

        self.messager = messenager
        
        viewcontainer = viewContainer(config)
        
        self.viewContainer = viewcontainer

        self.loadPics(config)
        
        # 准备阶段：展示cue，展示上次结果
        self.prepareProcess = PrepareProcess()
        self.prepareProcess.initial(self, viewcontainer, messenager)

        # 开始刺激：刺激时展示cue
        self.stimulateProcess = StimulateProcess()
        self.stimulateProcess.initial(self, viewcontainer, messenager)

        # 结束刺激：展示结果？
        self.finishProcess = FinishProcess()
        self.finishProcess.initial(self, viewcontainer, messenager)

        # Block间的空闲状态
        self.idleProcess = IdleProcess()
        self.idleProcess.initial(self, viewcontainer, messenager)

        self.currentProcess = self.idleProcess
        
        return self

    def loadPics(self,config):
    
        addSTI = config.addSTI
        win = visual.Window([1920, 1080], monitor="testMonitor", units="pix", fullscr=True,waitBlanking=True, color=(0, 0, 0), colorSpace='rgb255', screen=0,allowGUI=True)

        picAdd = os.listdir(addSTI)
        frameSet = []
        # initial frame
        add = config.addSTI + os.sep + 'initial_frame.png'
        initFrame = visual.ImageStim(win, image=add, pos=[0, 0], size=[
                                    1920, 1080], units='pix', flipVert=False)

        # stimulation frames

        for picINX in tqdm(range(len(picAdd)-2)):
            add = addSTI + os.sep + '%i.png' % picINX
            frame = visual.ImageStim(win, image=add, pos=[0, 0], size=[
                                        1920, 1080], units='pix', flipVert=False)
            frameSet.append(frame)

        self.viewContainer.w = win
        self.viewContainer.frameSet = frameSet
        self.viewContainer.initFrame = initFrame

        with open(addSTI+os.sep+'STI.pickle', "rb") as fp:
            self.viewContainer.targetPos = pickle.load(fp)

        return self
        
    def run(self):
        
        if self.end == False:
            self.currentProcess.run()
        else:
            self.w.close()
            core.quit()


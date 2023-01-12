import time 
from StimulationSystem.StimulationProcess.BasicStimulationProcess import BasicStimulationProcess
from psychopy import visual, core, event
import datetime
from psychopy.visual.circle import Circle
import matplotlib.pyplot as plt

class StimulateProcess(BasicStimulationProcess):
    def __init__(self) -> None:
        super().__init__()

    def update(self):
        
        self.controller.endBlock = self._checkBlock()
        
        
        self.initFrame.draw()
        self.controller.dialogue.draw()
        self.controller.feedback.draw()
        self.w.flip()

        # 增加另一个epoch
        self.controller.currentEpochINX += 1
        # 增加另一个epoch
        self.controller.epochThisBlock += 1
        pass

        
    def change(self,result):
        
        self.controller.currentProcess = self.controller.finishProcess
        self.controller.currentResult = result
        # 这里无需改变状态，因为在收到数据之后已经改变过了
        # self.eventController.sendEvent(251)
        self.eventController.clearEvent()



    def run(self):
        
        controller = self.controller
        self.w = controller.w
        
        message = 'STRD'
        self.messenager.send_exchange_message(message)
        print('\nStimulateProcess 发送开始检测指令，执行时间{}\n'.format(datetime.datetime.now()))
            
        frameINX = 0
        
        self.w.recordFrameIntervals = True
        self.w.refreshThreshold = 0.0005+1/60        
        startTime = core.getTime()
        # 发送trigger
        while frameINX < len(self.frameSet):

            if frameINX == 0:
                self.eventController.sendEvent(self.controller.cueEvent)
                
            self.frameSet[frameINX].draw()
            self.w.flip(False)
            
            frameINX += 1
            
        endTime = core.getTime()

        print('Overall trial dropped %i frames'%self.w.nDroppedFrames)

        self.w.frameIntervals = []
        self.w.recordFrameIntervals = False

        print("STI ended{}".format(endTime-startTime))
        
        self.initFrame.draw()
        self.controller.dialogue.draw()
        self.controller.feedback.draw()
        self.w.flip()
        
        self.eventController.clearEvent()
        while self.controller.currentProcess is self:
            # 如果刺激结束了，还没有收到结果，就先进入等待
            time.sleep(0.01)
            
        self.update()
        
        
    def _checkBlock(self):

        if self.controller.blockCueINX == []:
            self.controller.currentBlockINX += 1
            return True
        else:
            return False

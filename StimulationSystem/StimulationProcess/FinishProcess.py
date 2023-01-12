from numpy import place
from StimulationProcess.BasicStimulationProcess import BasicStimulationProcess
from psychopy.visual.rect import Rect
import time


class FinishProcess(BasicStimulationProcess):

    def __init__(self) -> None:
        super().__init__()


    def change(self):

        if self.controller.endBlock:
            self.controller.currentProcess = self.controller.idleProcess
            self.controller.historyString = []
        else:
            self.controller.currentProcess = self.controller.prepareProcess

    def run(self):
        
        # showFeedback 负责把判决结果显示在对话框
        
        id = self.events.index(self.controller.currentResult)
        self._showFeedback(id)
        
        self.change()

        pass

    def _showFeedback(self,currentResult):

        
        
        epochINX = self.controller.epochThisBlock    

        # result in this epoch 再画当前试次的结果
        resultChar = self.char[currentResult]
        resultChar = '%s'%(resultChar)
        # placeholder代表给之前的试次留空位
        placeholder = ''
        for _ in range(epochINX-1):
            placeholder = placeholder + ' '
        resultText = placeholder+resultChar
        
        charColor = 'white'
        result = self.drawDialogue(resultText, color=charColor,fillColor=None)
        
        self.initFrame.draw()
        self.controller.dialogue.draw()
        self.controller.feedback.draw()
        result.draw()
        self.w.flip()
        time.sleep(0.2)
        
        
        # 更新一下feedback，当前的feedback已经包含当前试次了，等待下一个试次再画上
        histroString = self.controller.historyString  
        feedbackText = ''.join(histroString)
        feedback = self.drawDialogue(feedbackText+resultChar,color='white',fillColor=None)
        self.controller.historyString.append(resultChar)
        self.controller.feedback = feedback
        

        return

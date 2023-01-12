import time
from StimulationProcess.BasicStimulationProcess import BasicStimulationProcess
from psychopy.visual.rect import Rect
from psychopy.visual.circle import Circle
from psychopy.visual import TextBox2
import matplotlib.pyplot as plt

class PrepareProcess(BasicStimulationProcess):
    def __init__(self) -> None:

        super().__init__()

    def change(self):

        # prepare --> stimulate
        self.controller.currentProcess = self.controller.stimulateProcess

    def run(self):
        # pop a cue
        self.controller.cueId = self.controller.blockCueINX.pop(0)
        self.controller.cueEvent = self.controller.blockCueEvent.pop(0)
        
        self.controller.w = self._showCue(self.controller.cueId)
        
        # 当前状态交给stimulate
        self.change()
        
    def _showCue(self, id):
        """
        draw initial texture and show result
        :return: None
        """
        self.initFrame.draw()
        self.controller.dialogue.draw()
        self.controller.feedback.draw()
        

        # rect
        pos = self.targetPos[id].position
        rect = Rect(win=self.w, pos=pos, width=140,
                    height=140, units='pix', fillColor='Red')
        rect.draw()
        self.w.flip()

        time.sleep(0.5)
        
        # circle
        circle = Circle(win=self.w, pos=[pos[0], pos[1]-90], radius=4, fillColor='Red', units='pix')
        circle.draw()
        self.initFrame.draw()
        self.controller.dialogue.draw()
        self.controller.feedback.draw()
        self.w.flip(False)
        time.sleep(0.1)
        
        circle.draw()
        self.initFrame.draw()
        self.controller.dialogue.draw()
        self.controller.feedback.draw()
        self.w.flip(False)
        
        return self.w
from abc import ABCMeta, abstractmethod
from psychopy.visual.circle import Circle
from psychopy import visual, core, event
from EventController import EventController

import time


class BasicStimulationProcess:

    def __init__(self) -> None:
        pass

    @abstractmethod
    def initial(self, controller, viewContainer, messenager):

        self.controller = controller
        self.messenager = messenager
        self.messenager.exchange_message_operator.controller = self.controller

        self.w = viewContainer.w

        self.initFrame = viewContainer.initFrame
        self.frameSet = viewContainer.frameSet

        self.controller.historyString = []
        self.char = viewContainer.char
        self.events = viewContainer.events
        self.targetPos = viewContainer.targetPos
        self.stringPos = viewContainer.stringPos
        self.paradigm = viewContainer.paradigm

        self.cueIndices = viewContainer.cueIndices
        self.cueEvents = viewContainer.cueEvents
        self.targetNUM = viewContainer.targetNUM
        self.cueText = viewContainer.displayChar
        self.COM = viewContainer.COM
        self.eventController = EventController(COM=self.COM)

        pass

    @abstractmethod
    def update(self):

        pass

    @abstractmethod
    def change(self):

        pass

    @abstractmethod
    def run(self):

        pass

    def drawDialogue(self, text, color, fillColor):

        dialogue = visual.TextBox2(
            self.w, text=text, font='Meslo LG M DZ', units='pix',
            pos=(-735, 525), letterHeight=50.0,
            size=(1470, 50), borderWidth=2.0,
            color=color, colorSpace='rgb',
            opacity=None,
            bold=False, italic=False,
            lineSpacing=1.0,
            padding=0.0, alignment='top-left',
            anchor='top-left',
            fillColor=fillColor, borderColor=None,
            editable=False,
            autoLog=True,)

        return dialogue


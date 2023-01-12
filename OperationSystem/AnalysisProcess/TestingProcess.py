from AnalysisProcess.BasicAnalysisProcess import BasicAnalysisProcess
import numpy as np
import pickle
import pandas as pd
import os

class TestingProcess(BasicAnalysisProcess):
    def __init__(self) -> None:
        super().__init__()


    def initial(self, controller=None, config=None, streaming=None, messenger=None):

        super().initial(controller, config, streaming, messenger)

        modelname = os.path.join(self.savepath, 'models/%sModel.pickle'%self.paradigm)

        if os.path.exists(modelname) and self.trainNUM!=0:
            self.loadModel(modelname)
            self.controller.trainFlag=True
        elif self.trainNUM == 0:
            self.algorithm = self.reTrainModel()
            with open(os.path.join(self.savepath, 'models/%sModel.pickle' % self.paradigm), "wb+") as fp:
                pickle.dump(self.algorithm, fp,protocol=pickle.HIGHEST_PROTOCOL)
            self.controller.trainFlag = True
        else:
            pass
        # 用来保存模型表现：ITR,accuracy
        self.scores = []
        # 用来保存每个trial的结果
        self.frames=[]

        return

    def reTrainModel(self):
        # train
        from AnalysisProcess.OperatorMethod.spatialFilter import TDCA

        with open(self.savepath+os.sep+'data/%sTrain.pickle'%self.paradigm, "rb") as fp:
            data = pickle.load(fp)

        trainX, trainy = np.concatenate(data['X']), np.concatenate(data['y'])

        model = TDCA(winLEN=self.winLEN, srate=self.srate,lag=self.lag)

        model.fit(trainX, trainy)

        return model


    def loadModel(self,modelname):

        with open(modelname,"rb") as fp:
            self.algorithm = pickle.load(fp)
        pass

    def run(self):

        # 同步系统,包含event

        while True:
            data = self.streaming.readFixedData(0, self.winLEN+self.lag)
            if data is not None:
                break

        epoch, event = data

        # 计算结果
        result = self.getResult(epoch)
        # 汇报结果
        self.controller.report(result)

        self.logger.success('Reported No.%s epoch,True event %s identified as %s'%(self.controller.     currentEpochINX,event,result))

        self._collectTest(epoch,event,result)

        self.controller.current_process = self.controller.wait_process
        self.messenger.state.current_detect_state = 'INIT'

        return

    def _collectTest(self,x,y,result):

        epochINX = self.controller.currentEpochINX
        blockINX = self.controller.currentBlockINX
        cueThisBlock = len(self.cueEvents[blockINX])

        # X: epoch * chn * T
        self.controller.testData['X'].append(x[np.newaxis,:,:])
        self.controller.testData['y'].append(y)
        # 保存结果
        self.controller.results.append(result)

        if (epochINX+1) % cueThisBlock == 0:

            self.controller.currentBlockINX += 1

            with open(os.path.join(self.savepath, 'data/%sTest.pickle' % self.paradigm), "wb+") as fp:
                pickle.dump(self.controller.testData, fp,
                            protocol=pickle.HIGHEST_PROTOCOL)

            self.peroformance()

        self.controller.currentEpochINX += 1

        return


    def peroformance(self):

        # 按照block为节奏记录结果
        from sklearn.metrics import accuracy_score
        from OperationSystem.AnalysisProcess.OperatorMethod.utils import ITR

        blockINX  = self.controller.currentBlockINX
        y = np.concatenate(self.controller.testData['y'])
        y_ = self.controller.results
        # 记录本block测试结果
        r = pd.DataFrame({
            'epochINX':np.arange(1,self.controller.currentEpochINX+2),
            'event':y,
            'eventChar':[self.config.char[self.config.events.index(i)] for i in y],
            'result':y_,
            'resultChar': [self.config.char[self.config.events.index(i)] for i in y_]
        })
        r['blockINX'] = blockINX
        r['subject'] = self.personName
        r['winLEN'] = self.winLEN
        r['ISI'] = self.config.ISI
        r['paradigm'] = self.paradigm


        self.frames.append(r)
        df = pd.concat(self.frames, axis=0, ignore_index=True)
        df.to_csv(self.savepath+os.sep+'record/%s_trackEpoch.csv'%self.paradigm)

        # 本block结果评估
        accuracy = accuracy_score(y,y_)
        itr = ITR(self.targetNUM, accuracy, self.winLEN)

        # 计算ITR
        f = pd.DataFrame({
            'accuracy': [accuracy],
            'itr':[itr],
            'winLEN':[self.winLEN],
            'subject':[self.personName],
            'block':[blockINX],
            'paradigm':[self.paradigm]
        })
        self.scores.append(f)
        df = pd.concat(self.scores, axis=0, ignore_index=True)
        df.to_csv(self.savepath+os.sep+'record/%s_online.csv'%self.paradigm)

        self.logger.success('Finished No.%s test block,accuracy:%s,ITR:%s'%(blockINX,accuracy,itr))

        return


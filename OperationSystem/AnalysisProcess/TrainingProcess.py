from AnalysisProcess.BasicAnalysisProcess import BasicAnalysisProcess
from AnalysisProcess.OperatorMethod.spatialFilter import TRCA,TDCA

import numpy as np
import pandas as pd
import pickle
import os

class TrainingProcess(BasicAnalysisProcess):
    def __init__(self) -> None:
        super().__init__()


    def run(self):

        # 训练过程,也会把event 标签传过来
        while True:
            data = self.streaming.readFixedData(0, self.winLEN+self.lag)
            if data is not None:
                break

        epoch, event = data

        # import matplotlib.pyplot as plt
        # plt.plot(epoch.T)
        # plt.show()

        # 在训练阶段没有真实的反馈，可以给“空格”反馈
        result = 30 if self.paradigm == 'wn' else 70

        print(result)
        # 汇报结果
        self.controller.report(result)

        # 储存当前Epoch
        self._collectTrain(epoch,event)

        self.logger.info('Training in process, No.%s epoch done,event:%s' %
                         (self.controller.currentEpochINX,event))
        # 训练模型
        if self.controller.trainFlag is True:
            self.trainModel()
            self.performance()
            self.viz()

        self.controller.current_process = self.controller.wait_process
        self.messenger.state.current_detect_state = 'INIT'
        return

    def _collectTrain(self,x,y):

        epochINX = self.controller.currentEpochINX

        # X: epoch * chn * T
        self.controller.trainData['X'].append(x[np.newaxis,:,:])
        self.controller.trainData['y'].append(y)

        if (epochINX+1) % self.targetNUM == 0:

            self.controller.currentBlockINX += 1

            with open(os.path.join(self.savepath, 'data/%sTrain.pickle'%self.paradigm), "wb+") as fp:
                pickle.dump(self.controller.trainData, fp,
                            protocol=pickle.HIGHEST_PROTOCOL)

        self.controller.currentEpochINX += 1

        if (epochINX+1) >= self.trainNUM:
            self.controller.trainFlag = True

        return

    def performance(self):

        from tqdm import tqdm
        self.logger.success('Evaluating offline performance...')
        from sklearn.model_selection import LeaveOneOut
        from OperationSystem.AnalysisProcess.OperatorMethod.utils import ITR

        X = self.controller.trainData['X']
        y = self.controller.trainData['y']
        X,y = np.concatenate(X),np.concatenate(y)


        X = np.stack([X[y == i] for i in np.unique(y)])
        y = np.stack([y[y == i] for i in np.unique(y)])

        # classification
        X = np.transpose(X, axes=(1, 0, -2, -1))
        y = np.transpose(y, axes=(-1, 0))

        loo = LeaveOneOut()
        loo.get_n_splits(X)
        frames = []

        for cv, (train_index, test_index) in tqdm(enumerate(loo.split(X))):

            X_train, X_test = np.concatenate(
                X[train_index]), np.concatenate(X[test_index])
            y_train, y_test = np.concatenate(
                y[train_index]), np.concatenate(y[test_index])

            for winLEN in np.arange(0.1,self.winLEN+0.1,0.1):
                model = TDCA(winLEN=winLEN, lag=self.lag,srate=self.srate,
                montage=self.targetNUM,n_band=self.n_band)
                model.fit(X_train,y_train)
                accuracy = model.score(X_test, y_test)
                itr = ITR(self.targetNUM, accuracy, winLEN)
                f = pd.DataFrame({
                    'subject':[self.personName],
                    'winLEN':[winLEN],
                    'accuracy': [accuracy],
                    'paradigm':[self.paradigm],
                    'cv':[cv],
                    'ITR': [itr]
                })

                frames.append(f)

            df = pd.concat(frames,axis=0,ignore_index=True)
            df.to_csv(self.savepath+os.sep+'record/%s_offline.csv'%self.paradigm)

        pass

    def viz(self):

        import seaborn as sns
        import matplotlib.pyplot as plt
        frames = []
        d = os.listdir(self.savepath+os.sep+'record')
        for f in d:
            if f.split('_')[-1]=='offline.csv':
                df = pd.read_csv(self.savepath+os.sep+'record/%s'%f)
                frames.append(df)
        frames = pd.concat(frames,axis=0,ignore_index=True)

        sns.set_theme(style='ticks')
        f,(ax1,ax2) = plt.subplots(2,1)
        sns.lineplot(data=frames,x='winLEN',y='accuracy',hue='paradigm',ax=ax1)
        sns.lineplot(data=frames,x='winLEN',y='accuracy',hue='paradigm',ax=ax2)
        plt.tight_layout()
        f.savefig(self.savepath+os.sep+'images/offline.png',dpi=400)
        plt.close()

    def trainModel(self):

        model = TDCA(winLEN=self.winLEN,srate=self.srate)

        trainX = self.controller.trainData['X']
        trainy = self.controller.trainData['y']

        trainX, trainy = np.concatenate(trainX), np.concatenate(trainy)

        model.fit(trainX, trainy)

        self.controller.testing_process.algorithm = model

        # with open(os.path.join(self.savepath, 'models/%sModel.pickle'%self.paradigm), "wb+") as fp:
        #     pickle.dump(model, fp,
        #         protocol=pickle.HIGHEST_PROTOCOL)

        return


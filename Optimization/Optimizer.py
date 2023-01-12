import os
import pickle
import numpy as np
from loguru import logger
from tqdm import tqdm
import seaborn as sns
import scipy.io as scio
import matplotlib.pyplot as plt


class Optimizier():

    def __init__(self, config, dataStreaming,tobeOpt=True) -> None:

        self.personName = config.personName
        # 默认保存在Operation里
        self.fatherAdd = 'OperationSystem/ResultStored'
        self.prepareFolder()
        self.streaming = dataStreaming

        self.config = config

        self.srate = config.srate
        self.winLEN = config.winLEN
        self.lag = config.lag
        self.n_band=config.n_band

        self.optWIN = config.optWIN
        T = int(self.srate*(self.optWIN+self.lag))

        self.epochNUM = int(config.classNUM * config.optBlockNUM)
        self.classNUM = config.classNUM
        self.blockNUM = config.optBlockNUM
        self.epochINX = 0
        self.chnNUM = config.chnNUM

        self.data = dict(
            X=np.zeros((self.epochNUM,self.chnNUM,T)),
            y=np.zeros(self.epochNUM)
        )

        self.logger = logger

        # 是否需要采数据
        self.tobeOpt = tobeOpt

        if self.tobeOpt:
            self.streaming.start()
            self.pbar = tqdm(total=self.classNUM, desc="No.1 Block")
            self.endFlag = False
        else:
            self.logger.success('No need for online data collection')
            self.endFlag = True

        pass


    def prepareFolder(self):
        fatherAdd = self.fatherAdd
        sonAdd = os.path.join(fatherAdd,self.personName)
        if not os.path.exists(sonAdd):
            os.makedirs(os.path.join(sonAdd, 'images'))
            os.makedirs(os.path.join(sonAdd, 'models'))
            os.makedirs(os.path.join(sonAdd, 'data'))
            os.makedirs(os.path.join(sonAdd, 'record'))
            os.makedirs(os.path.join(sonAdd, 'stimulus'))
        self.savepath = sonAdd
        return


    def collectData(self):

        while True:
            data = self.streaming.readFixedData(0, self.optWIN+self.lag)
            if data is not None:
                break

        self.data['X'][self.epochINX] = data[0]
        self.data['y'][self.epochINX] = data[1]

        self.epochINX += 1
        self.pbar.update(1)

        if (self.epochINX) >= self.epochNUM:
            self.endFlag = True

        self.saveData()

    def saveData(self):

        if self.epochINX % self.classNUM == 0:
            with open(os.path.join(self.savepath, 'data/2bOptimized.pickle'), "wb+") as fp:
                pickle.dump(self.data, fp, protocol=pickle.HIGHEST_PROTOCOL)
            self.logger.success('Saved %s/%s block' %
                                ((self.epochINX//self.classNUM), self.blockNUM))
            if self.endFlag:
                self.pbar.close()
                self.streaming.disconnect()

            else:
                self.pbar.desc = 'No.%s Block'%((self.epochINX//self.classNUM)+1)
                self.pbar.reset()
        else:
            pass


    def optimize(self):

        import random
        import pandas as pd
        from sklearn.model_selection import LeaveOneOut
        from sklearn.metrics import accuracy_score
        from OperationSystem.AnalysisProcess.OperatorMethod.spatialFilter import TDCA
        # load data
        with open(self.savepath+os.sep+'data/2bOptimized.pickle', "rb") as fp:
            data = pickle.load(fp)

        X,y = data['X'],data['y']
        self._classes = np.unique(y).tolist()
        codespace = self.config.classNUM
        targetNUM = self.config.targetNUM

        # pick seeds
        pickedSet = []
        for seed in range(self.config.seedNUM):
            random.seed(seed)
            pickedSet.append({
            'seed':seed,
            'code':random.sample(self._classes, targetNUM)
        })

        self.logger.info('Calculating response function')
        # plot TRF
        self.IRF(X,y)

        X = np.stack([X[y == i] for i in np.unique(y)])
        y = np.stack([y[y == i] for i in np.unique(y)])

        X = np.transpose(X,axes=(1,0,-2,-1))
        y = np.transpose(y,axes=(-1,0))


        loo = LeaveOneOut()
        loo.get_n_splits(X)
        frames = []

        for cv, (train_index, test_index) in enumerate(loo.split(X)):

            X_train, X_test = np.concatenate(
                X[train_index]), np.concatenate(X[test_index])
            y_train, y_test = np.concatenate(
                y[train_index]), np.concatenate(y[test_index])

            for winLEN in np.arange(0.1,self.winLEN+0.3,0.1):

                commonModel = TDCA(winLEN=winLEN, lag=self.lag,
                                srate=self.srate, montage=codespace,n_band=self.n_band)
                commonModel.fit(X_train,y_train)
                acc = commonModel.score(X_test,y_test)
                coefMatrix = commonModel.rho
                labels = np.arange(targetNUM)

                S = []
                seeds = []
                for codeset in tqdm(pickedSet):
                    picked = [self._classes.index(i) for i in codeset['code']]
                    picked_coef = coefMatrix[picked, :][:, picked]
                    s = accuracy_score(labels, np.argmax(picked_coef, axis=0))
                    S.append(s)
                    seeds.append(codeset['seed'])

                f = pd.DataFrame(data=S, index=seeds,)
                f.reset_index(level=0, inplace=True)
                f = f.melt(id_vars='index', value_name='score',
                            var_name='cv')
                f = f.rename(columns={'index': 'seed'})

                f['cv'] = cv
                f['winLEN'] = winLEN
                f['SCORE']=acc

                frames.append(f)

        frames = pd.concat(frames,ignore_index=True,axis=0)
        frames['subject'] = self.personName

        frames.to_csv(os.path.join(self.savepath, 'record/codeset.csv'))
        # frames = pd.read_csv(os.path.join(self.savepath, 'record/codeset.csv'))
        # plot performance
        self.performance(frames)
        # pick best
        bestCodeset = self.pickOptimal(frames,pickedSet)
        bestCodeset = {'WN':bestCodeset.T}

        scio.savemat(os.path.join(
            self.savepath, 'stimulus/%s.mat' % self.personName),bestCodeset)
        self.logger.success('Picked optimized codeset')


        return

    def pickOptimal(self,frames,pickset):


        path = 'Optimization/STI.mat'
        S = scio.loadmat(path)['wn']

        ave = frames[frames.winLEN == self.winLEN].groupby(
            'seed', as_index=False).mean()
        bestSeed = ave.loc[ave['score'].argmax()].seed
        bestCode = [c for c in pickset if c['seed'] == bestSeed][0]['code']

        bestCodeset = S[[self._classes.index(i) for i in bestCode]]

        return bestCodeset

    def performance(self,frames):

        sns.set_theme(style='ticks')
        f,(ax1,ax2) = plt.subplots(1,2)

        sns.lineplot(data=frames,x='winLEN',y='score',ax=ax1)
        sns.histplot(data=frames[frames.winLEN==self.winLEN],x='score',kde=True,bins=30,ax=ax2)

        f.savefig(self.savepath+os.sep+'images/optimizePerformance.png')

        return

    def IRF(self,X,y):

        from OperationSystem.AnalysisProcess.OperatorMethod.modeling import Code2EEG
        import scipy.io as scio
        from scipy.signal import resample
        # stimulus
        path = 'Optimization/STI.mat'
        S = scio.loadmat(path)['wn']
        S = resample(S, self.optWIN*self.srate, axis=-1)

        lag = int(self.lag * self.srate)
        winLEN = int(self.optWIN * self.srate)
        X = X[..., :winLEN]
        _classes = np.unique(y)
        code2EEG = Code2EEG(srate=self.srate, winLEN=self.optWIN, tmin=0, tmax=0.5, S=(
            S, _classes), estimator=0.95, padding=True, n_band=1, component=1)

        code2EEG.fit(X, y)

        trf = code2EEG.trf.squeeze()

        t = np.linspace(0, 0.5, trf.shape[-1])
        sns.set_theme(style='ticks')
        f,ax = plt.subplots()
        ax.plot(t,trf)
        ax.set_xlabel('Lag(s)')
        ax.set_ylabel('Amp(a.u.)')
        ax.set_title('%s'%self.personName)
        f.savefig(self.savepath+os.sep+'images/trf.png',dpi=300)
        plt.close()

        return

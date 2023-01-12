import numpy as np
import matplotlib.patches as patches
from StimulationSystem.UICreator.StimTargetRect import StimTargetRect
import matplotlib.pyplot as plt
import os
import pickle
import matplotlib
import shutil
from tqdm import tqdm
matplotlib.use('agg')
    
class frameLoader():
    def __init__(self) -> None:

        self.initFrame = None
        self.frameSet = None
        self.rectSet = None
        self.stringPositions = None

        pass


def fig2data(f):
    """
    fig = plt.figure()
    image = fig2data(fig)
    @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
    @param fig a matplotlib figure
    @return a numpy 3D array of RGBA values
    """
    import PIL.Image as Image
    # draw the renderer
    f.canvas.draw()

    # Get the RGBA buffer from the figure
    w, h = f.canvas.get_width_height()
    buf = np.fromstring(f.canvas.tostring_argb(), dtype=np.uint8)
    buf.shape = (w, h, 4)

    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = np.roll(buf, 3, axis=2)
    image = Image.frombytes("RGBA", (w, h), buf.tostring())
    image = np.asarray(image)
    return image


class UIFactory:

    def __init__(self,config):

        self.rowNUM,self.columnNUM = config.layout
        self.x_resolution, self.y_resolution = config.resolution
        self.refreshRate = config.refreshRate
        self.stiLEN = config.stiLEN
        
        self.maxFrames = int(self.refreshRate*self.stiLEN)

        self.frequency = config.frequency
        self.phase = config.phase
        self.charSet = config.char

        self.cubicSize = config.cubicSize
        self.interval = config.interval
        self.initWidth, self.initHeight = config.trim
        self.paradigm = config.paradigm
        self.personName = config.personName

        self.saveFolder = os.path.join(
            os.getcwd(), 'StimulationSystem', 'pics', self.paradigm)
        if os.path.exists(self.saveFolder) is True:
            shutil.rmtree(self.saveFolder)
            os.makedirs(self.saveFolder)
        else:
            os.makedirs(self.saveFolder)
    
    def getFrames(self):

        frequenctSet = np.array(
            self.frequency).reshape((self.columnNUM, self.rowNUM))
        phaseSet = np.array(self.phase).reshape(
            (self.columnNUM, self.rowNUM))

        rectSet = []
        # 刺激大小
        for colINX, (freqCol, phaseCol) in enumerate(zip(frequenctSet, phaseSet)):
            for rowINX, (freq, phase) in enumerate(zip(freqCol, phaseCol)):
                # 左下角
                target_site_point = [(colINX*(self.cubicSize+self.interval)+self.initWidth), ((
                    self.rowNUM-rowINX-1)*(self.cubicSize+self.interval)+self.initHeight)]
                
                rectINX = colINX*self.rowNUM+rowINX

                rectSet.append(StimTargetRect(self.paradigm, rectINX, self.personName, target_site_point, self.cubicSize, self.refreshRate,freq, phase, 255))

        frameSet = []

        # 聊天框
        init_x = self.initWidth
        init_y = self.initHeight+self.rowNUM*(self.cubicSize+self.interval)-20
        stringPositions = [(init_x-self.x_resolution//2+320),
                           (init_y-self.x_resolution//2-10)]


        
        for N in tqdm(range(self.maxFrames+1)):
            # 从此循环进入每一帧
            f = plt.figure(figsize=(19.20, 10.80), facecolor='none', dpi=100)
            plt.xlim(0, 1)
            plt.ylim(0, 1)
            plt.gca().xaxis.set_major_locator(plt.NullLocator())
            plt.gca().yaxis.set_major_locator(plt.NullLocator())
            plt.subplots_adjust(top=1, bottom=0, left=0,
                                right=1, hspace=0, wspace=0)

            plt.rcParams['axes.unicode_minus'] = False  # 这两行需要手动设置
            current_axis = plt.gca()
            
            # change order 
            # charSet = np.reshape(self.charSet,(self.columnNUM,self.rowNUM),order='F').flatten()
            charSet = self.charSet
            for rect,char in zip(rectSet,charSet):
                # 每一帧的每一个目标
                if N == 0:
                    brightness = 1
                else:
                    brightness = rect.cal_brightness(N)
                x_loc = rect.site_point[0] / self.x_resolution
                y_loc = rect.site_point[1] / self.y_resolution
                x_size = rect.rect_size / self.x_resolution
                y_size = rect.rect_size / self.y_resolution

                # 画一个正方形
                target = patches.Rectangle((x_loc,y_loc),
                                         x_size,y_size,
                                         linewidth=1, facecolor=[brightness, brightness, brightness])
                # 写上字
                v = plt.text(x_loc + x_size / 2,
                             y_loc + y_size / 2, char,
                             fontsize=30, horizontalalignment='center', verticalalignment='center')
                current_axis.add_patch(target)

            plt.axis('off')
            frameSet.append(fig2data(f))
            plt.close(f)
        
        frames = frameLoader()
        frames.initFrame = frameSet.pop(0)
        frames.frameSet = frameSet
        frames.rectSet = rectSet
        frames.stringPositions = stringPositions

        return frames


    def saveFrames(self,frames):

        frameSet = frames.frameSet
        for i,frame in enumerate(frameSet):
            plt.imsave(self.saveFolder+os.sep+'%i.png' % i, frame)

        initFrame = frames.initFrame
        plt.imsave(self.saveFolder+os.sep+'initial_frame.png', initFrame)

        rectSet = frames.rectSet
        with open(self.saveFolder+os.sep+'STI.pickle', "wb+") as fp:
            pickle.dump(rectSet, fp, protocol=pickle.HIGHEST_PROTOCOL)

        




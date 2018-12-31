%matplotlib
# import the seaborn module which is based on matplotlib to make our visualization more presentable
import seaborn as sns

# set the default style
sns.set()
from __future__ import print_function
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from matplotlib.image import AxesImage
import numpy as np
import matplotlib.pyplot as plt

class MyPlot(object):

    def makePlot(self):
        self.selected_x_points=np.array([])
        self.selected_y_points=np.array([])
        self.index=np.array([])
        self.fig = plt.figure('Test')
        self.ax = plt.subplot(111)
        self.x = np.array([1,2,0,1,5,9,3,7])
        self.y = np.array([2,4,1,2,3,5,7,1])
        #self.ax.plot(self.x, self.y, '-', color='red')
        self.ax.plot(self.x, self.y, 'o', color='blue', picker=5)
        self.selected_points()

    def onPick(self, event=None):
        ind=event.ind
        if len(np.argwhere(self.index==ind[0]))>0:
            self.selected_x_points=np.delete(self.selected_x_points,[np.argwhere(self.index==ind)])
            self.selected_y_points=np.delete(self.selected_y_points,[np.argwhere(self.index==ind)])
            self.index=np.delete(self.index,[np.argwhere(self.index==ind)])
        else:
            self.index=np.append(self.index,ind)
            self.selected_x_points=np.append(self.selected_x_points,self.x[ind])
            self.selected_y_points=np.append(self.selected_y_points,self.y[ind])
        print("selected x points",self.selected_x_points)
        print("selected y points",self.selected_y_points)
        self.highlight.set_data(self.selected_x_points,self.selected_y_points)
        self.fig.canvas.draw_idle()
        
    def selected_points(self):
        self.highlight, = self.ax.plot([], [], 'o', color='yellow')
        self.cid = plt.connect('pick_event', self.onPick)
        plt.show()

if __name__ == '__main__':
    app = MyPlot()
    app.makePlot()

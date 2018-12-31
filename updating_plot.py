from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QTextCharFormat
from PyQt5.QtWidgets import (QApplication, QCalendarWidget, QCheckBox,
        QComboBox, QDateEdit, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
        QLayout, QWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtCore, QtWidgets

from numpy import arange, sin, pi

from matplotlib.figure import Figure
import os
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget


g=0
class ApplicationWindow(QtWidgets.QWizard):
    def __init__(self):
        super().__init__()
        self.addPage(p0_intro())
        self.addPage(p1_settings())
        self.button(QtWidgets.QWizard.NextButton).clicked.connect(self.nextButtonFunction)
        self.setWindowTitle("GMRT Observation Planning Wizard")

    def nextButtonFunction(self):
        global g,dc
        if self.currentId()==1:
            g=g+1
            print('next is clicked')
            dc.update_figure()
            #MyStaticMplCanvas(self.main_widget, width=5, height=2, dpi=100).update_figure(self)

class p0_intro(QtWidgets.QWizardPage):
    """
    Introductory page. Selections to move between different type 
    selections can be done from here
    """
    def __init__(self):
        super().__init__()  
        self.icon=QPixmap("data/images/gmrt.png")
        self.icon=self.icon.scaled(380,480)
        self.setTitle("Welcome")
        self.label=QtWidgets.QLabel("This wizard will help you to select the pointings and generate the command files for your upcoming survey observation."
           " Click next to proceed.")
        self.setPixmap(QtWidgets.QWizard.WatermarkPixmap, self.icon) #left side banner, pixel size needs to be matched with the pixel size of the box
        self.label.setWordWrap(True)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout) 


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None):
        global fig,axes
        fig = Figure()
        axes = fig.add_subplot(111)
        super().__init__(fig)  


class p1_settings(QtWidgets.QWizardPage):
    def __init__(self):
        global dc
        super().__init__()
        self.main_widget = QWidget(self)
        l = QVBoxLayout(self.main_widget)
        dc = MyDynamicMplCanvas()
        l.addWidget(dc)
        self.main_widget.resize(540,240)
        self.resize(540,240)


class MyDynamicMplCanvas(MyMplCanvas):
    def update_figure(self):
        global fig,axes
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        l = [random.randint(0, 40) for i in range(4)]
        axes.cla()
        axes.plot([0, 1, 2, 3], l, 'r')
        self.draw()



if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    wizard = ApplicationWindow()
    wizard.show()
    sys.exit(app.exec_())





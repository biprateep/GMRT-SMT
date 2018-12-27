"""
Prepare for observations in an interactive way.
@author: biprateep
"""
import os
import random
import sys
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
import sqlite3 as sql
from astropy.coordinates import SkyCoord
from astropy import units as u
from astroplan import Observer, FixedTarget
from astropy.time import Time
import matplotlib.pyplot as plt
from pytz import timezone
from PyQt5.QtCore import QDate, QDateTime, Qt
from PyQt5.QtWidgets import (QApplication, QCalendarWidget, QCheckBox,
        QComboBox, QDateEdit, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
        QLayout, QWidget, QMainWindow, QMenu, QVBoxLayout,  QSizePolicy, QMessageBox)

q=0


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None):
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)  

class p2_graphSelect(QtWidgets.QWizardPage):
    def __init__(self):
        super().__init__()
        global dc,q
        self.main_widget = QWidget(self)
        l = QVBoxLayout(self.main_widget)
        dc = MyDynamicMplCanvas()
        l.addWidget(dc)
      
    
class grab_params():
    def grabParams(self,date):
        global dc
        """
        Grab the input Parameters from the previous form
        """
        self.passed_date=QDate(date).toPyDate()
        dc.update_figure(self.passed_date)

class MyDynamicMplCanvas(MyMplCanvas):

    def update_figure(self,passed_date):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        #l = [random.randint(0, 40) for i in range(4)]
        self.observatory_parameter(passed_date)
        self.axes.cla()
        '''self.axes.plot([0, 1, 2, 3], l, 'r')
        self.draw()'''
        self.createPlot()

    def observatory_parameter(self,passed_date):
        """
        Initialise the basic set up required, connect to DB, grab data from DB to Dataframe, etc
        """
        self.conn=sql.connect("main.db")    #Connect to the DB
        self.c=self.conn.cursor()             #Create the cursor
        self.pointList=pd.read_sql("SELECT * FROM pointList",self.conn)
        self.pointList=pd.read_sql("SELECT * FROM pointList",self.conn)
        self.pointList['pColor'] = np.where(self.pointList['obs']==1.0, 'r', 'b') # Make color list for observed and unbserved
        self.pointings=SkyCoord(ra=self.pointList.ra,dec=self.pointList.dec)
        self.name=self.pointList.name
        """
        Observatory Parameters: Coordinates and elevation angle for GMRT observatory
        GMRT coordinates from http://gmrt.ncra.tifr.res.in/gmrt_hpage/Users/doc/manual/Manual_2013/manual_20Sep2013.pdf

        """
        self.obsLoc = Observer(longitude=74.05*u.deg, latitude=19.1*u.deg, elevation=588*u.m, name="GMRT", timezone="Asia/Kolkata")
        self.obsHor=17.0 #elivation angle for horizon of observer
        print(passed_date)
        self.obsTime = Time(['%s 00:00:01'%(passed_date)]) #Time obtained from the calendar widget
        
        """
        Rise and set time calculations, astropy takes in IST time zone but returns as UTC
        So need to convert them back to IST
        """
        self.riseT = self.obsLoc.target_rise_time(self.obsTime, self.pointings, which='next',horizon=self.obsHor*u.deg).datetime
        self.riseT=[timezone("UTC").localize(a) for a in self.riseT] #adding the UTC tzinfo to python datetime obect
        self.riseT=[a.astimezone(timezone("Asia/Kolkata")) for a in self.riseT] #Timezone change
        self.riseT=[i.strftime('%H:%M:%S') for i in self.riseT]

        self.setT = self.obsLoc.target_set_time(self.obsTime, self.pointings, which='next',horizon=self.obsHor*u.deg).datetime
        self.setT=[timezone("UTC").localize(a) for a in self.setT]
        self.setT=[a.astimezone(timezone("Asia/Kolkata")) for a in self.setT]
        self.setT=[i.strftime('%H:%M:%S') for i in self.setT]
        
        #Setting up the GUI
        #self.setTitle("Select the pointings to be ordered")
        #self.grabParams(5) #Need to implement
        #self.createPlot() #create the plot for selection of pointings        
        #layout = QtWidgets.QGridLayout() #initialise the layout for the plotbox, so that it can be added as a single unit to the wizard page
        #layout.addWidget(self.plotBox, 0, 0)
        #self.setLayout(layout)
     
    
    
    def createPlot(self):
        print('asd')
        """
        Main function to create the plotting and selection window
        """
        #self.plotBox = QtWidgets.QGroupBox("Click in the order you want them to be observed") #set up the box to fit in the plot and toolbar
        #self.fig, self.ax = plt.subplots() #get the axis, figure and canvas obects
        self.canvas=FigureCanvas(self.fig)
        
        #custom legend
        self.legend_elements = [Line2D([0], [0], marker='o', markeredgecolor='r', linestyle="None", label='Observed',markerfacecolor='None', markersize=5), Line2D([0], [0], marker='o', markeredgecolor='b',linestyle="None", label='Unobserved', markerfacecolor='None', markersize=5),]                   
        self.axes.legend(handles=self.legend_elements)
        #sc=self.axes.scatter(np.array([1,2]),np.array([2,3]))
        #Make the scatter plot
        sc=self.axes.scatter(self.pointings.ra.degree,self.pointings.dec.degree,marker='o',facecolors=[(1,1,1,1) for i in range(len(self.pointList['pColor']))],edgecolors=self.pointList['pColor'],picker=0.5)
        self.axes.grid()
        self.draw()
        
        
        #Make annotations to display pointing name and rise and set time
        
        #Parameters to change the looks of the annotation
        self.annot = self.axes.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"),arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        
        def update_annot(ind):
            """
            Function to update the annotations with the required text
            """
            self.pos = sc.get_offsets()[ind["ind"][0]]
            self.annot.xy = self.pos
            text = "{}\nRise:{}\nSet:{}".format(", ".join([self.name[p] for p in ind["ind"]]), ", ".join([self.riseT[p] for p in ind["ind"]]), ", ".join([self.setT[p] for p in ind["ind"]]))
            self.annot.set_text(text)
            self.annot.get_bbox_patch().set_facecolor("white")
            self.annot.get_bbox_patch().set_alpha(1)

        def hover(event):
            """
            Function to get the annotation on hovering
            """
            vis = self.annot.get_visible()
            if event.inaxes == self.axes:
                cont, ind = sc.contains(event)
                if cont:
                    update_annot(ind)
                    self.annot.set_visible(True)
                    self.fig.canvas.draw_idle()
                else:
                    if vis:
                        self.annot.set_visible(False)
                        self.fig.canvas.draw_idle()
        #Recurring handlers for dynamic events like hover and click
        self.fig.canvas.mpl_connect("motion_notify_event", hover)
        
        
        self.canvas.draw() #Draw the plot
        self.toolBar=NavigationToolbar(self.canvas,self) #Create the matplotlib tool bar
        
        #Put the design elements in the plotbox
        self.plotLayout = QtWidgets.QGridLayout()
        self.plotLayout.addWidget(self.canvas, 0, 0)#, Qt.AlignCenter)
        self.plotLayout.addWidget(self.toolBar, 1, 0)
        #self.plotBox.setLayout(self.plotLayout) 
        

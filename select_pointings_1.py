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
from matplotlib.widgets import LassoSelector
import numpy as np
import pandas as pd
import sqlite3 as sql
from PyQt5.QtWidgets import QScrollArea
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
from matplotlib.path import Path
from cmdFile import genCmdFile

class p3_graphSelect(QtWidgets.QWizardPage):

    def __init__(self):
        super().__init__()
        widget =  QWidget(self)
        vlay = QVBoxLayout(widget)
        m = WidgetPlot(self)
        vlay.addWidget(m)

class WidgetPlot(QWidget):

    def __init__(self, *args, **kwargs):
        global canvas,label
        QWidget.__init__(self, *args, **kwargs)
        canvas = PlotCanvas(self)
        self.toolbar = NavigationToolbar(canvas, self)
        self.layout = QGridLayout()
        self.layout.addWidget(canvas,0,0)
        self.layout.addWidget(self.toolbar,1,0)
        self.layout.setColumnMinimumWidth(0,600)
        self.layout.setColumnMinimumWidth(1,400)
        self.layout.setRowMinimumHeight(1,50)
        self.setLayout(self.layout)
        self.initUI()


    def createLayout_Container(self):
        global canvas,label
        label=QtWidgets.QLabel("")
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignJustify)
        self.scrollarea = QScrollArea(self)
        self.scrollarea.setFixedWidth(400)
        self.scrollarea.setWidgetResizable(True)
        widget = QWidget()
        self.scrollarea.setWidget(widget)
        self.layout_SArea = QVBoxLayout(widget)
        self.layout_SArea.addWidget(label)

    def initUI(self):
        global canvas,label
        self.createLayout_Container()
        self.layout.addWidget(self.scrollarea,0,1)
        self.show()


        

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None):
        global q,fig,ax
        fig = Figure()
        FigureCanvas.__init__(self, fig)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        ax = fig.add_subplot(111)


 
class grab_params():

    def grabParams(self,date):
        global dc,label
        label.setText("Click on the points to select the fields.\nFor group selection lasso over the points with the right click. \nThe selected points will appear here.")

        """
        Grab the input Parameters from the previous form
        """
        self.passed_date=QDate(date).toPyDate()
        self.observatory_parameter(self.passed_date)


    def observatory_parameter(self,passed_date):
        global q,fig,ax,canvas
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
        
        self.createPlot() #create the plot for selection of pointings        



    def createPlot(self):
        global fig,ax,canvas
        ax.cla()
        """
        Main function to create the plotting and selection window
        """
        
        #custom legend

        
        self.legend_elements = [Line2D([0], [0], marker='o', markeredgecolor='r', linestyle="None", label='Observed',markerfacecolor='None', markersize=5), Line2D([0], [0], marker='o', markeredgecolor='b',linestyle="None", label='Unobserved', markerfacecolor='None', markersize=5),]                   
        ax.legend(handles=self.legend_elements)

        #Make the scatter plot
        self.sc=ax.scatter(self.pointings.ra.degree,self.pointings.dec.degree,marker='o',facecolors=[(1,1,1,1) for i in range(len(self.pointList['pColor']))],edgecolors=self.pointList['pColor'],picker=1)
        ax.set_title("Select the pointings to be ordered")
        fig.tight_layout()
        ax.grid(alpha=0.25)


        #Highlight/remove the selected/deselected points
        self.selected_x_points=np.array([])
        self.selected_y_points=np.array([])
        self.selected_fields  =np.array([])
        self.selected_fields_rise_set=np.array([['  Field-id    ','  Rise time   ','Set time']])
        self.index=np.array([])
        self.highlight, = ax.plot([], [], 'o',markersize=4.5, color='black',alpha=0.7)
        canvas.draw() #Draw the plot


        #Make annotations to display pointing name and rise and set time
        
        #Parameters to change the looks of the annotation
        self.annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points", bbox=dict(boxstyle="round", fc="w"),arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)
        
        def update_annot(ind):
            global q,fig,ax,canvas
            """
            Function to update the annotations with the required text
            """
            self.pos = self.sc.get_offsets()[ind["ind"][0]]
            self.annot.xy = self.pos
            text = "{}\nRise:{}\nSet:{}".format(", ".join([self.name[p] for p in ind["ind"]]), ", ".join([self.riseT[p] for p in ind["ind"]]), ", ".join([self.setT[p] for p in ind["ind"]]))
            #print(text)
            self.annot.set_text(text)
            self.annot.get_bbox_patch().set_facecolor("white")
            self.annot.get_bbox_patch().set_alpha(1)
        
        def hover(event):
            global q,fig,ax,canvas
            """
            Function to get the annotation on hovering
            """
            vis = self.annot.get_visible()
            if event.inaxes == ax:
                cont, ind = self.sc.contains(event)
                if cont:
                    update_annot(ind)
                    self.annot.set_visible(True)
                    canvas.draw_idle()
                else:
                    if vis:
                        self.annot.set_visible(False)
                        fig.canvas.draw_idle()
        #Recurring handlers for dynamic events like hover and click
        fig.canvas.mpl_connect("motion_notify_event", hover)
        
        def onPick(event):
            global q,fig,ax,canvas,label
            ind=event.ind 
            #print(ind)
            if len(np.argwhere(self.index==ind[0]))>0:
                self.selected_x_points=np.delete(self.selected_x_points,[np.argwhere(self.index==ind)])
                self.selected_y_points=np.delete(self.selected_y_points,[np.argwhere(self.index==ind)])
                self.selected_fields  =np.delete(self.selected_fields,[np.argwhere(self.index==ind)])
                self.selected_fields_rise_set=np.delete(self.selected_fields_rise_set,[np.argwhere(self.index==ind)+1],axis=0)
                self.index=np.delete(self.index,[np.argwhere(self.index==ind)])
            else:
                self.index=np.append(self.index,ind)
                self.selected_x_points=np.append(self.selected_x_points,self.pointings.ra.degree[ind])
                self.selected_y_points=np.append(self.selected_y_points,self.pointings.dec.degree[ind])
                self.selected_fields  =np.append(self.selected_fields,   self.name[ind])
                self.selected_fields_rise_set=np.append(self.selected_fields_rise_set,np.array([[self.name[ind[0]],self.riseT[ind[0]],self.setT[ind[0]]]]),axis=0)
            #print("selected fields",self.selected_fields)
            '''print("selected fields rise",self.selected_fields_rise)
            print("selected fields set",self.selected_fields_set)
            print("selected x points",self.selected_x_points)
            print("selected y points",self.selected_y_points,'\n\n')'''
            self.highlight.set_data(self.selected_x_points,self.selected_y_points)
            label.setText([np.array2string(self.selected_fields_rise_set, separator='             ',suffix='   ')][0])

        fig.canvas.mpl_connect("pick_event", onPick)

        #Recurring handlers for selection by Lasso-selection by right-clicking 
        def onselect(verts):
            global selected_x_points,index,selected_y_points
            self.path = Path(verts)
            self.ind = np.nonzero(self.path.contains_points(np.column_stack((self.pointings.ra.degree,self.pointings.dec.degree))))[0]
            for i in self.ind:
                if len(np.argwhere(i==self.index))>0:
                    self.selected_x_points=np.delete(self.selected_x_points,np.argwhere(i==self.index))
                    self.selected_y_points=np.delete(self.selected_y_points,np.argwhere(i==self.index))
                    self.selected_fields  =np.delete(self.selected_fields,np.argwhere(i==self.index))
                    self.selected_fields_rise_set=np.delete(self.selected_fields_rise_set,[np.argwhere(i==self.index)+1],axis=0)
                    self.index=np.delete(self.index,np.argwhere(i==self.index))
                else:
                    self.index=np.append(self.index,i)
                    self.selected_x_points=np.append(self.selected_x_points,self.pointings.ra.degree[i])
                    self.selected_y_points=np.append(self.selected_y_points,self.pointings.dec.degree[i])
                    self.selected_fields  =np.append(self.selected_fields,   self.name[i])
                    self.selected_fields_rise_set=np.append(self.selected_fields_rise_set,np.array([[self.name[i],self.riseT[i],self.setT[i]]]),axis=0)
            self.highlight.set_data(self.selected_x_points,self.selected_y_points)
            label.setText([np.array2string(self.selected_fields_rise_set, separator='             ',suffix='   ')][0])
            canvas.draw_idle() 
        self.lasso = LassoSelector(ax, onselect=onselect,button=3)

        canvas.draw() #Draw the plot
     


        

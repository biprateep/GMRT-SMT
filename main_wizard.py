import sys
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QIcon
from select_pointings_1 import p3_graphSelect,grab_params   #wizard page to do graphical selection of pointings
from cmdFile import genCmdFile
from astropy.utils import iers
from astropy.time import Time
import astropy.units as u
from astroplan import download_IERS_A
from PyQt5.QtCore import QDate, QLocale, Qt
from PyQt5.QtGui import QFont, QTextCharFormat, QPalette, QColor
from PyQt5.QtWidgets import (QApplication, QCalendarWidget, QCheckBox,
        QComboBox, QDateEdit, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
        QLayout, QWidget, QFileDialog)


class Window(QtWidgets.QWizard):
    def __init__(self):
        super().__init__()
        self.addPage(p1_intro_page())
        self.d=p2_Date_Para_page()
        self.addPage(self.d)
        self.addPage(p3_graphSelect())
        self.button(QtWidgets.QWizard.NextButton).clicked.connect(self.nextButtonFunction)
        self.button(QtWidgets.QWizard.FinishButton).clicked.connect(self.finishButtonFunction)
        self.setWindowTitle("PAWS: Observation Planning Wizard")
        self.resize(1100,650)
    def nextButtonFunction(self):
        if self.currentId()==2:
            self.draw_graph=grab_params()
            self.draw_graph.grabParams(self.d.calendar.selectedDate())
    def finishButtonFunction(self):
        self.path=path_cmdFile()
        genCmdFile(self.d.calendar.selectedDate().toString(Qt.ISODate),self.d.obsTimeLineEdit.text(),
                   self.d.subarrayLineEdit.text(),self.d.dataLocationLineEdit.text(),self.path.outPath,self.draw_graph.selected_fields)
        print("\nFile saved successfully at:   %s \n\nTHANK YOU FOR USING PAWS!\n"%(self.path.outPath))

class p1_intro_page(QtWidgets.QWizardPage):
    """
    Introductory page. Selections to move between different type 
    selections can be done from here
    """
    def __init__(self):
        super().__init__()  
        self.icon=QPixmap("data/images/gmrt.png")
        self.icon=self.icon.scaled(380,480)
        self.setPixmap(QtWidgets.QWizard.WatermarkPixmap, self.icon) #left side banner, pixel size needs to be matched with the pixel size of the box
       
        self.setTitle("Welcome")
        self.label=QtWidgets.QLabel("This wizard will help you to select the pointings and generate the command files for your upcoming survey observation."
           " Click next to proceed.")
        self.label.setWordWrap(True)
        # for setting colour
        pal = QPalette(self.label.palette())
        pal.setColor(QPalette.WindowText, QColor(Qt.black))
        self.label.setPalette(pal) 

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout) 

  
class p2_Date_Para_page(QtWidgets.QWizardPage):
    def __init__(self):
        super().__init__() 
        self.createPreviewGroupBox()
        self.createDatesGroupBox()
        self.createParamBox()

        self.layout = QGridLayout()
        self.layout.addWidget(self.previewGroupBox, 0, 0)
        self.layout.addWidget(self.datesGroupBox, 1, 0)
        self.layout.addWidget(self.paramBox, 0, 1)
        self.layout.setColumnMinimumWidth(0,600)     
        self.setLayout(self.layout)

        self.layout.setColumnStretch(0, 0.6)
        self.layout.setColumnStretch(1, 2)
        self.layout.setRowStretch(0, 2)
        self.layout.setRowStretch(1, 0.75)

    def selectedDateChanged(self):
        self.currentDateEdit.setDate(self.calendar.selectedDate())
    def createPreviewGroupBox(self):
        self.previewGroupBox = QGroupBox("Preview")
        self.calendar = QCalendarWidget()
        self.calendar.setMinimumDate(QDate(1900, 1, 1))
        self.calendar.setMaximumDate(QDate(3000, 1, 1))
        self.calendar.setGridVisible(True)
        self.previewLayout = QGridLayout()
        self.previewLayout.addWidget(self.calendar, 0, 0)
        self.previewGroupBox.setLayout(self.previewLayout)
 
    def createDatesGroupBox(self):
        self.datesGroupBox = QGroupBox(self.tr("Dates"))

        self.currentDateEdit = QDateEdit()
        self.currentDateEdit.setDisplayFormat('MMM dd yyyy')
        self.currentDateEdit.setDate(self.calendar.selectedDate())
        self.currentDateEdit.setDateRange(self.calendar.minimumDate(),
                self.calendar.maximumDate())

        self.currentDateLabel = QLabel("&Current Date:")
        self.currentDateLabel.setBuddy(self.currentDateEdit)

        self.currentDateEdit.dateChanged.connect(self.calendar.setSelectedDate)
        self.calendar.selectionChanged.connect(self.selectedDateChanged)
 
        dateBoxLayout = QGridLayout()
        dateBoxLayout.addWidget(self.currentDateLabel, 1, 0)
        dateBoxLayout.addWidget(self.currentDateEdit, 1, 1)
        dateBoxLayout.setRowStretch(1, 1)

        self.datesGroupBox.setLayout(dateBoxLayout)

    def createParamBox(self):
        global q
        
        self.paramBox=QtWidgets.QGroupBox("Enter Observation Parameters")
        
        self.startFreqLabel = QtWidgets.QLabel("Start Frequency")
        self.startFreqLineEdit = QtWidgets.QLineEdit()
        self.startFreqLineEdit.setPlaceholderText("in MHz")
        self.startFreqLineEdit.setToolTip("Frequency in units of MHz")
        self.startFreqLabel.setBuddy(self.startFreqLineEdit)
        
        self.bandwidthLabel = QtWidgets.QLabel("Bandwidth")
        self.bandwidthLineEdit = QtWidgets.QLineEdit()
        self.bandwidthLineEdit.setPlaceholderText("in MHz")
        self.bandwidthLineEdit.setToolTip("in units of MHz")
        self.bandwidthLabel.setBuddy(self.bandwidthLineEdit)
        
        self.samplingTimeLabel = QtWidgets.QLabel("Sampling Time")
        self.samplingTimeLineEdit = QtWidgets.QLineEdit()
        self.samplingTimeLineEdit.setPlaceholderText("in micro seconds")
        self.samplingTimeLineEdit.setToolTip("in units of micro seconds")
        self.samplingTimeLabel.setBuddy(self.samplingTimeLineEdit)
        
        self.obsTimeLabel = QtWidgets.QLabel("Observation Time")
        self.obsTimeLineEdit = QtWidgets.QLineEdit()
        self.obsTimeLineEdit.setPlaceholderText("per Pointing in minutes")
        self.obsTimeLineEdit.setToolTip("Observation time per pointing in minutes")
        self.obsTimeLabel.setBuddy(self.obsTimeLineEdit)
        
        self.dataLocationLabel = QtWidgets.QLabel("Data Location")
        self.dataLocationLineEdit = QtWidgets.QLineEdit()
        self.dataLocationLabel.setBuddy(self.dataLocationLineEdit)
        
        self.projectCodeLabel = QtWidgets.QLabel("Project Code")
        self.projectCodeLineEdit = QtWidgets.QLineEdit()
        self.projectCodeLineEdit.setPlaceholderText("GTAC Project Code")
        self.projectCodeLineEdit.setToolTip("GTAC Project Code")
        self.projectCodeLabel.setBuddy(self.projectCodeLineEdit)
        
        self.subarrayLabel = QtWidgets.QLabel("Subarray")
        self.subarrayLineEdit = QtWidgets.QLineEdit(self)
        self.subarrayLabel.setBuddy(self.subarrayLineEdit)
        
        self.paramLayout = QtWidgets.QGridLayout()
        
        
        self.paramLayout.addWidget(self.startFreqLabel, 0, 0)
        self.paramLayout.addWidget(self.startFreqLineEdit, 0, 1)
        
        self.paramLayout.addWidget(self.bandwidthLabel, 1, 0)
        self.paramLayout.addWidget(self.bandwidthLineEdit, 1, 1)
        
        self.paramLayout.addWidget(self.samplingTimeLabel, 2, 0)
        self.paramLayout.addWidget(self.samplingTimeLineEdit, 2, 1)
        
        self.paramLayout.addWidget(self.obsTimeLabel, 3, 0)
        self.paramLayout.addWidget(self.obsTimeLineEdit, 3, 1)
        
        self.paramLayout.addWidget(self.dataLocationLabel, 4, 0)
        self.paramLayout.addWidget(self.dataLocationLineEdit, 4, 1)
        
        self.paramLayout.addWidget(self.projectCodeLabel, 5, 0)
        self.paramLayout.addWidget(self.projectCodeLineEdit, 5, 1)
        
        self.paramLayout.addWidget(self.subarrayLabel, 6, 0)
        self.paramLayout.addWidget(self.subarrayLineEdit, 6, 1)
        self.paramBox.setLayout(self.paramLayout)
 


   
class path_cmdFile(QtWidgets.QWizardPage):
    def __init__(self):
        super().__init__()
        self.saveFileDialog()

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.outPath, _ = QFileDialog.getSaveFileName(self,"Saving the command file","cmdFile.txt","All Files (*);;Text Files (*.txt)", options=options)


#####App framework stops here##################

def checkIERS(warn_update=14*u.day):
    """
    Function to check whether the latest IERS tables are present. Else downloads it.
    Taken from the astropy utils.py source code! Dated: 01/08/2018
    """
    
    try:
        
        currentTime = Time.now()
        table = iers.IERS_Auto.open()
        index_of_last_observation = ''.join(table['PolPMFlag_A']).index('IP')
        time_of_last_observation = Time(table['MJD'][index_of_last_observation],format='mjd')
        time_since_last_update = Time.now() - time_of_last_observation
        
        if int(currentTime.mjd)*u.day not in iers.IERS_Auto.open()['MJD']:
            print("IERS tables are outdated! Downloading latest table...")
            download_IERS_A()
     
        if warn_update < time_since_last_update:
            print("IERS tables are outdated! Downloading latest table...")
            download_IERS_A()
            
        if int(currentTime.mjd)*u.day in iers.IERS_Auto.open()['MJD']:
            print("Latest IERS tables are present. Proceeding...")
    except:
        print("Could not download latest IERS tables.\n Rise and Set time will be error prone.")
        

if __name__ == '__main__':
    checkIERS()
    app = QtWidgets.QApplication(sys.argv)
    wizard = Window()
    wizard.show()
    sys.exit(app.exec_())


"""
Command file generator code for PAWS. Mostly taken from the code base of SMT.
This code generates a GWB command file for IA beams as per the selection made by the astronomer. This version is based on Nilesh's
cmd file for GWBH4 which is capable of taking data from 30 antennas.

FOR NOW CAN ONLY HANDLE SEQUENTIAL IA OBSERVATIONS. PHASING, PA beams, Known pulsars to be added later on.

NOTE:
1.Each line of command file cannot be more than 70 characters name of file to be saved in cannot 
be longer than 50 characters

2. For now the source list has been named "psr_survey_points.list"

3. 
The code also generates a list of the selected sources in the GMRT format and also plots the plan

by Biprateep Dey
mail: biprateep@gmail.com
"""


def genCmdFile(date,obsTime,subA,dataLoc,outPath,field_id):
    j=0
    """
    Generates the command file based on trackListToDo of main file.
    date is taken from the global variable date used to generate the To-Do List
    observation time(obsTime) is to be given in minutes
    
    list of inputs:
        date: date of observation as selected by observer
        outPath: output file path including the file name.
        field_id: list of the names of the pointings
        obsTime: time length of each observation in minutes
        dataLoc: location to save the data
        subarray: usual value 4
    """
    f_out=open(outPath,'w')        
    f_out.write("*COMMAND FILE FOR OBSERVATION ON "+date+'\n')
    f_out.write("*OBSERVATION TIME:  "+str(obsTime)+'m EACH\n\n')
    f_out.write('cmode 1\n')
    f_out.write('lnkndasq\n\n')
    f_out.write('subar '+str(subA)+'\n\n')
    f_out.write('goout\n')
    f_out.write('gosacout\n\n')
    f_out.write('*goin\n')
    f_out.write('*gosacin\n\n')
    f_out.write("*standard gmrt source list\n\n")
    f_out.write("addlist \'/odisk/gtac/source/psr_updated_24sep15.list'\n\n")
    f_out.write("*please check the sourcelist is placed in the below directory\n\n")
    f_out.write("addlist \'/odisk/gtac/source/u34_075_sources.list\'\n\n") #the list destination may be brought out later on
    f_out.write("*ALL LINES UPTO THIS HAS TO BE PRESERVED\n\n")
    
    for name in field_id: 
            
        f_out.write("*POINTING: "+str(j+1)+" NAME: "+str(name)+"\n\n")        
        f_out.write("gts \'"+str(name)+"\'\n")
        f_out.write("sndsacsrc(1,12h)\n")
        f_out.write("sndsacsrc(1,12h)\n")
        f_out.write("stabct\n")
        f_out.write("/(gotosrc 15m)\n\n")
        f_out.write("strtndasc\n")
        f_out.write("/gwbpsr.start "+dataLoc+" "+str(name)+"\n")
        f_out.write("time "+str(obsTime)+"m\n")
        f_out.write("/gwbpsr.stop\n")
        f_out.write("stpndasc\n")
        f_out.write("time 3s\n\n")
        j+=1
    f_out.write("*ALL LINES AFTER THIS HAS TO BE PRESERVED\n\n")
    f_out.write("end")
    f_out.close()   



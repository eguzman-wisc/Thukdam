# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 15:02:41 2018

@author: guzman
"""

#!/usr/bin/python

import os
import mne
import sys
import re
import logging


# Set up a logger to track progress of code
logger = logging.getLogger('Crop_Log')


# Ensures that certain information gets outputted to the user, while information needed for Debugging gets outputted to a log file. Log File created in script directory
if not logger.handlers:
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('cropper.log', mode = 'w')
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.DEBUG)
    c_format = logging.Formatter('%(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m-%d-%Y %H:%M:%S' )
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    logger.setLevel(logging.DEBUG)

# Begin running actual program code 
logger.debug('----------------------------------------INITIATING-----------------------------------------')

logger.info('Cropper.py\nVersion: 0.9\nCreated 11/14/2018\nCopyright 2018 Board of Regents of University of Wisconsin System\n')

logger.info('Running File...\n')


# Measures how many arguments used when calling program, if none, throws error. If input and output filenames aren't called, error is thrown 
args = sys.argv
numargs = len(sys.argv) - 1     # -1 because [0] = self

logger.debug('Arguments read\n')
logger.info('%s arguments applied\n', numargs)

logger.debug('Checking if number of agruments called meets minimal requirement of input file and mmn/abr output file names (minimum number of arguments = 3)...\n')

if numargs == 0:
    logger.error('No arguments provided. Must provide input and output file names\n')
    logger.info('Possible arguments include:\n  --infile=[filename.bdf] or a complete file path (e.g Y:/study/year/folder/filename.bdf)\n  --mmn_outfile=[filename.fif]\n  --abr_outfile=[filename.fif]\n  --mmn_pad=[#.##] (Default if no arg: 0.5 sec)\n  --abr_pad=[#.##] (Default if no arg: 0.1 sec)\n  --keep_all_channels (Default if no arg: keeps only first 7 channels)\n')
    sys.exit(0)
elif numargs < 3:
     logger.error('Not enough arguments provided. Must at least provide 1 input file and 2 output file names.\n')
     sys.exit(0)


# Checks for specific argument format. 1 input filename must be indicated in .bdf format, else error will be thrown, and 2 output file names must be indicated in .fif format else error thrown (other arguments optional)
infile = [s for s in args if '.bdf' in s]
outfiles = [s for s in args if '.fif' in s]

logger.debug('Checking if input and outfile arguments are in proper format (need 1 .bdf input file, and 2 .fif output file names)...\n')

logger.debug('Looking for .bdf files...\n')
if infile == []:
    logger.error('Input file name must be in .bdf format, please enter name correctly.\n')
    sys.exit(0)

if len(infile) > 2:
    logger.error('More than 1 .bdf input file called, please indicate only 1 .bdf file to crop. Output filenames should be in .fif format\n')
    sys.exit(0)
   
logger.debug('.bdf input file found\n')

logger.debug('Looking for .fif files...\n')
if outfiles == []:
    logger.error('Output file names must be in .fif format, please enter names correctly.\n')
    sys.exit(0)
    
if len(outfiles) != 2:
    logger.error('Please indicate only 2 different output file names in .fif format. One MMN file and one ABR file.\n')
    sys.exit(0)
    
logger.debug('Both .fif output file names found\n')
  
if numargs == 3:
    logger.warning('Only input and output filenames included in arguments. mmn_pad defaulted to 0.5 sec, abr_pad defaulted to 0.1 sec, and only first 7 channels in data will be kept\n')
    
    
# Checks if input file exists in current directory, or input path, if it doesn't throws error
logger.debug('Extracting input file name or input file path from arguments\n')
input_file = next(s for s in args if '.bdf' in s)
infile_string = input_file.split('=')
fname = infile_string[1]  

logger.debug('Extracted file name/path = %s\n', fname)

logger.debug('Finding input file or file directory\n')

if os.path.isabs(os.path.realpath(fname)) == True:
    fdir = os.path.dirname(fname)
    os.chdir(fdir)      #changes current working directory to file directory
    if os.path.isfile(os.path.basename(fname)) == False:
        logger.error('Input file does not exist in indicated directory, please input a different file name, or a correct file path\n')
        sys.exit(0)
    fname = os.path.basename(fname)
    logger.debug('Input file found within indicated path\n')
elif os.path.isfile(fname) != True:
     logger.error('Input file does not exist in current directory, please input different file namr, or a complete file path (Use "/" not "\\")\n')
     sys.exit(0)  
    
logger.info('Input file exists\n')


# Lists to user their called arguments, if user sees error, they can exit and restart program, else program continues with inputted arguments
position = 1  
logger.info('All inputted arguments listed below...')
while (numargs >= position):  
    print ("  parameter %i: %s" % (position, sys.argv[position]))
    position = position + 1

logger.debug('Asking user if all inputted arguments are correct...\n') 
correct = raw_input("Are all arguments correct? [y/n]: ")
while (len(correct) >= 1):
    if correct.upper() == 'Y':
        logger.debug('User indicated arguments are correct\n')
        break
    elif correct.upper() == 'N': 
        logger.debug('User indicated arguments are incorrect\n')
        print("\nPlease restart program with arguments wanted.\n")
        sys.exit(0)
    else:
        logger.debug('User entered an answer other than "Y" or "N", asked to re-enter a proper response\n')
        print("\nPlease enter a proper response.")
        correct = raw_input("Are all arguments correct? [y/n]: ")
        

# Reads raw data and begins finding beginning and end of each MMN and ABR event
logger.info('Preparing file...\n')

logger.debug('Begin reading input file info\n')
raw = mne.io.read_raw_edf(fname)
logger.info('Input file overview: %s\n', raw)

logger.info('File cropper initializing...\n')

logger.info('Finding MMN and ABR events in data...\n')
events = mne.find_events(raw, stim_channel="STI 014", output='step', shortest_event=1)

logger.info('MMN and ABR events found. Cropping file...\n')


# Identifies if user indicated specific padding times (time left before and after first and last event found) for mmn and abr files. If no argument, Default values used mmn_pad = 0.5sec and abr_pad = 0.1sec
logger.debug('Extracting MMN and ABR padding times from arguments\n')
mmnt = next((s for s in args if 'mmn_pad' in s),None)
abrt = next((s for s in args if 'abr_pad' in s),None)

logger.debug('Finding mmn_pad time\n')
if mmnt == None:
    mmn_pad = 0.5
    logger.debug('No mmn_pad argument found, MMN padding defaulted to 0.5 sec\n')
else:
    mmn_pad = float(re.findall("\d+\.\d+", mmnt)[0])
    logger.debug('Extracted mmn_pad time = %s sec\n', mmn_pad)
    
logger.info('MMN padding time = %s sec\n', mmn_pad)

logger.debug('Finding abr_pad time\n')
if abrt == None:
    abr_pad = 0.1
    logger.debug('No abr_pad argument found, ABR padding defaulted to 0.1 sec\n')
else:
    abr_pad = float(re.findall("\d+\.\d+", abrt)[0])
    logger.debug('Extracted abr_pad time = %s sec\n', abr_pad)
    
logger.info('ABR padding time = %s sec\n', abr_pad)

       
# Cropping of each event file with indicated padding times
logger.info('Splitting MMN and ABR events, and removing unwanted data...\n')
x = 0

logger.debug('Finding all MMN events using the frequency at which MMN events occur freq_mmn < freq_abr...\n')
while events[x+2,0] - events[x,0] > raw.info['sfreq']/3:
    x += 1
    continue

logger.debug('All MMN events found. Creating dataset of all channels during MMN + padding timeframe\n')
raw_mmn = raw.copy().crop((events[0,0]/raw.info['sfreq']) - mmn_pad, (events[x-1,0]/raw.info['sfreq']) + mmn_pad)
  
logger.info('All MMN data found.\n')

y = x  

logger.debug('Finding all ABR events using the frequency at which ABR events occur freq_mmn < freq_abr...\n')
while events[y+2,0] - events[y,0] < raw.info['sfreq']/10:
    y += 1
    if len(events) < y+3:
        break
    else: 
        continue

logger.debug('All ABR events found. Creating dataset of all channels during ABR + padding timeframe\n')
raw_abr = raw.copy().crop((events[x,0]/raw.info['sfreq']) - abr_pad, (events[y+1,0]/raw.info['sfreq']) + abr_pad)

logger.info('All ABR data found.\n')

logger.info('Time cropping finished. Finalizing MMN and ABR files for output...\n')


# Splitting MMN data in half to reduce Memory usage when loading
raw_mmna = raw.copy().crop(0,len(raw_mmn)/(3*raw.info['sfreq']))

raw_mmnb = raw.copy().crop(len(raw_mmn)/(3*raw.info['sfreq']),(2*len(raw_mmn))/(3*raw.info['sfreq']))

raw_mmnc = raw.copy().crop((2*len(raw_mmn))/(3*raw.info['sfreq']),len(raw_mmn)/raw.info['sfreq'])



# Loads file data in order to modify data
logger.debug('Loading all MMN and ABR channel data for modification of channels\n')
raw_mmna.load_data()
raw_mmnb.load_data()
raw_mmnc.load_data()
logger.debug('MMN data loaded.\n')
raw_abr.load_data()
logger.debug('ABR data loaded.\n')


# Identifies if user indicated to keep all the channels, if no keep_all_channels argument inputted. Default is to only keep the first 7 channels
logger.debug('Checking if arguments asked to keep all channels in output files\n')
keep = next((s for s in args if 'keep_all' in s),None)

logger.info('Dropping unneeded channels...\n')

if keep == None:
    logger.debug('No argument to keep all channels found, only first 7 channels will be kept in output files\n')
    logger.debug('Dropping extra channels from MMN data\n')
    
    cropped_mmn = raw_mmna.drop_channels(['EXG1-0', 'EXG2-0', 'EXG3-0', 'EXG4-0', 'EXG5-0', 'EXG6-0', 'Resp', 'Temp', 'EXG7', 'EXG8'])
    
    cropped_mmnb = raw_mmnb.drop_channels(['EXG1-0', 'EXG2-0', 'EXG3-0', 'EXG4-0', 'EXG5-0', 'EXG6-0', 'Resp', 'Temp', 'EXG7', 'EXG8'])
    
    cropped_mmnc = raw_mmnc.drop_channels(['EXG1-0', 'EXG2-0', 'EXG3-0', 'EXG4-0', 'EXG5-0', 'EXG6-0', 'Resp', 'Temp', 'EXG7', 'EXG8'])
    
    cropped_mmn.append([cropped_mmnb,cropped_mmnc])
    
    logger.info('MMN file ready for output.\n')
    
    logger.debug('Dropping extra channels from ABR data\n')
    
    cropped_abr = raw_abr.drop_channels(['EXG1-0', 'EXG2-0', 'EXG3-0', 'EXG4-0', 'EXG5-0', 'EXG6-0', 'Resp', 'Temp', 'EXG7', 'EXG8'])
    logger.info('ABR file ready for output.\n')
else:
    logger.debug('Argument to keep all channels found, no channels will be dropped from output files.\n')
    
    cropped_mmn = raw_mmn.copy()
    cropped_abr = raw_abr.copy()
    logger.info('No channels dropped. MMN and ABR files ready for output.\n')   

logger.info('Creating output files with cropped data...\n')


# MMN and ABR files created and saved based on output argument naming conventions
logger.debug('Extracting output file names from arguments\n')
mmnout = next(s for s in args if 'mmn_outfile' in s)
mmn_outstring = mmnout.split('=')
mmn_outfile = mmn_outstring[1]
logger.debug('MMN output file name found. File name = %s\n', mmn_outfile)

abrout = next(s for s in args if 'abr_outfile' in s)
abr_outstring = abrout.split('=')
abr_outfile = abr_outstring[1]
logger.debug('ABR output file name found. File name = %s\n', abr_outfile)

logger.info('Saving output file data...\n')

cropped_mmn.save(mmn_outfile, overwrite=True)
cropped_abr.save(abr_outfile, overwrite=True)
logger.debug('MMN and ABR output files saved, if file with same name already existed in file directory, that file was overwritten\n')

logger.info('MMN and ABR cropped output files have been created.\n')

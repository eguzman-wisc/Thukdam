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
import pyedflib
import numpy
from itertools import chain

# Set up a logger to track progress of code
logger = logging.getLogger('Crop_Log')


# Ensures that certain information gets outputted to the user, while information needed for Debugging gets outputted to a log file. Log File created in script directory.
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
logger.debug('\n----------------------------------------INITIATING-----------------------------------------\n')

logger.info('\n   Cropper.py\n   Version: 0.9.2\n   Created 12/05/2018\n   Copyright 2018 Board of Regents of University of Wisconsin System\n')

logger.info('Running File...\n')


# Measures how many arguments used when calling program, if none, throws error. If input and output filenames aren't called, error is thrown 
args = sys.argv
numargs = len(sys.argv) - 1     # -1 because [0] = self

logger.debug('Arguments read\n')
logger.info('%i arguments applied\n', numargs)

logger.debug('Checking if number of agruments called meets minimal requirement of input file and mmn/abr output file names (minimum number of arguments = 3)...\n')

if numargs == 0:
    logger.error('No arguments provided. Must provide input and output file names\n')
    logger.info('Possible arguments include:\n   --infile=[filename.bdf] or a complete file path (e.g Y:/study/year/folder/filename.bdf)\n   --mmn_outfile=[filename.bdf]\n   --abr_outfile=[filename.bdf]\n   --mmn_pad=[#.##] (Default if no arg: 0.5 sec)\n   --abr_pad=[#.##] (Default if no arg: 0.1 sec)\n   --keep_all_channels (Default if no arg: keeps only first 6 EEG channels and event channel)\n')
    sys.exit(0)
elif numargs < 3:
     logger.error('Not enough arguments provided. Must at least provide 1 input file and 2 output file names.\n')
     sys.exit(0)


# Checks for specific argument format. 1 input filename must be indicated in .bdf format, else error will be thrown, and 2 output file names must be indicated in .bdf format else error thrown (other arguments optional). 
infile = [s for s in args if 'infile' in s]
outfiles = [s for s in args if 'outfile' in s]
bdf_files = [s for s in args if '.bdf' in s]

logger.debug('Checking if input and outfile arguments are in proper format (need 1 .bdf input file, and 2 .bdf output file names)...\n')

logger.debug('Looking for input file...\n')
if infile == []:
    logger.error('Input file name must be in .bdf format, please enter name correctly.\n')
    sys.exit(0)

if len(infile) != 1:
    logger.error('Please indicate only 1 input file name in .bdf format you wish to crop.\n')
    sys.exit(0)
   
logger.debug('Input file to crop found\n')

logger.debug('Looking for output files...\n')
if outfiles == []:
    logger.error('Output file names must be in .bdf format, please enter names correctly.\n')
    sys.exit(0)
    
if len(outfiles) != 2:
    logger.error('Please indicate only 2 different output file names in .bdf format. One MMN file and one ABR file.\n')
    sys.exit(0)
    
logger.debug('Both output file names found\n')

if len(bdf_files) != 3:
    logger.error('Please indicate all file formats in .bdf format. 1 input file to crop, and 2 output file names to save MMN and ABR data to.\n')
    sys.exit(0)
    
logger.debug('All 3 files in .bdf format.\n')

# If only the 3 necessary arguments are called (input and output files), user is warned that all other values will be defaulted
if numargs == 3:
    logger.warning('Only input and output filenames included in arguments. mmn_pad defaulted to 0.5 sec, abr_pad defaulted to 0.1 sec, and only first 6 EEG and event channels in data will be kept\n')
    
    
# Checks if input file exists in current directory, or input path, if it doesn't throws error
logger.debug('Extracting input file name or input file path from arguments\n')
input_file = next(s for s in args if 'infile' in s)
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


# Lists to user their called arguments, if user sees error, they can exit and restart program, else program continues with inputted arguments.
position = 1  
logger.info('All inputted arguments listed below...')
while (numargs >= position):  
    logger.info('Parameter %i: %s', position, sys.argv[position])
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
        

# Reads raw data and begins finding beginning and end of each MMN and ABR events.
logger.info('Preparing file...\n')

logger.debug('Begin reading input file info\n')
raw = mne.io.read_raw_edf(fname, verbose = False)
logger.info('Input file overview: %s\n', raw)

logger.info('File cropper initializing...\n')

logger.info('Finding MMN and ABR events in data...\n')
events = mne.find_events(raw, stim_channel="STI 014", output='step', shortest_event=1)  # STI 014 is channel with event signals

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
logger.debug('Identifying data sampling rate...\n')
freq = raw.info['sfreq']
logger.info('Data sampling rate = %s Hz\n', freq)

logger.info('Splitting MMN and ABR events, and removing unwanted data...\n')
x = 0

logger.debug('Finding all MMN events using the frequency at which MMN events occur freq_mmn < freq_abr...\n')
while events[x+2,0] - events[x,0] > freq/3:
    x += 1
    continue

logger.debug('All MMN events found. Creating dataset of all channels during MMN + padding timeframe\n')
raw_mmn = raw.copy().crop(float((events[0,0]/freq) - mmn_pad), float((events[x-1,0]/freq) + mmn_pad))
  
logger.info('All MMN data found.\n')

y = x  

logger.debug('Finding all ABR events using the frequency at which ABR events occur freq_mmn < freq_abr...\n')
while events[y+2,0] - events[y,0] < freq/10:
    y += 1
    if len(events) < y+3:
        break
    else: 
        continue

logger.debug('All ABR events found. Creating dataset of all channels during ABR + padding timeframe\n')
raw_abr = raw.copy().crop((events[x,0]/freq) - abr_pad, (events[y+1,0]/freq) + abr_pad)

logger.info('All ABR data found.\n')

logger.info('Time cropping finished. Finalizing MMN and ABR files for output...\n')


# Splitting MMN data in thirds to reduce Memory usage when loading
logger.debug('Splitting MMN data into 3 parts to reduce memory usage when loading data...\n')
raw_mmna = raw_mmn.copy().crop(0,len(raw_mmn)/(3*freq))

raw_mmnb = raw_mmn.copy().crop(len(raw_mmn)/(3*freq),(2*len(raw_mmn))/(3*freq))

raw_mmnc = raw_mmn.copy().crop((2*len(raw_mmn))/(3*freq),round(len(raw_mmn)/freq,1))

logger.debug('MMN data split into 3 equal parts\n')


# Loads file data in order to modify data
logger.debug('Loading all MMN and ABR channel data for modification of channel information\n')
raw_mmna.load_data()
raw_mmnb.load_data()
raw_mmnc.load_data()
logger.debug('MMN data loaded.\n')
raw_abr.load_data()
logger.debug('ABR data loaded.\n')


# Identifies if user indicated to keep all the channels, if no keep_all_channels argument inputted. Default is to only keep the first 6 EEG channels and the event channel
logger.debug('Checking if user asked to keep all channels in output files\n')
keep = next((s for s in args if 'keep_all' in s),None)

if keep == None:
    logger.info('Dropping unneeded channels...\n')
    logger.debug('No argument to keep all channels found, only first 6 EEG channels and event channel will be kept in output files\n')
    logger.debug('Dropping extra channels from MMN data....\n')
    
    cropped_mmn = raw_mmna.drop_channels(['EXG1-0', 'EXG2-0', 'EXG3-0', 'EXG4-0', 'EXG5-0', 'EXG6-0', 'Resp', 'Temp', 'EXG7', 'EXG8'])
    
    cropped_mmnb = raw_mmnb.drop_channels(['EXG1-0', 'EXG2-0', 'EXG3-0', 'EXG4-0', 'EXG5-0', 'EXG6-0', 'Resp', 'Temp', 'EXG7', 'EXG8'])
    
    cropped_mmnc = raw_mmnc.drop_channels(['EXG1-0', 'EXG2-0', 'EXG3-0', 'EXG4-0', 'EXG5-0', 'EXG6-0', 'Resp', 'Temp', 'EXG7', 'EXG8'])
    
    logger.debug('Combining the three MMN parts to save to output file...\n')
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


# Gets output filenames from called arguments
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


# Gets input bdf file header from raw data file to use in the created MMN and ABR files
logger.debug('Reading input file header information to save into MMN and ABR files...\n')
infile_info = pyedflib.EdfReader(fname)


# Creates MMN .bdf data file from cropped MMN data using pyedflib module
logger.debug('Begin writing MMN data to .bdf file.\n')
m = pyedflib.EdfWriter(mmn_outfile, len(cropped_mmn.info['ch_names']), file_type=pyedflib.FILETYPE_BDF)

logger.info('Creating file: %s with %i channels.\n', mmn_outfile, len(cropped_mmn.info['ch_names']))

logger.debug('Writing input file header info into MMN header\n')
header = infile_info.getHeader()
m.setHeader(header)

logger.info('Creating individual channel headers...\n')
x = 0
mmn_chan_data = []

logger.debug('Writing individual channel headers in accordance to respective channels on input file...\n')
for x in xrange(0,len(cropped_mmn.info['ch_names'])):
    dict = infile_info.getSignalHeader(x)
    mmn_chan_info = {'label': dict['label'], 'dimension': 'mV', 'sample_rate': freq, 'physical_max': 1.0, 'physical_min': -2.0, 'digital_max': 8388607, 'digital_min': -8388608, 'prefilter': dict['prefilter'], 'transducer': dict['transducer']}
    
    # If not all channels are kept, indexing is not kept the same for event channel, so an excpetion has to be made to keep the event channel with a proper header
    if x == len(cropped_mmn.info['ch_names']):
        dict = infile_info.getSignalHeader(16)
        mmn_chan_info = {'label': dict['label'], 'dimension': 'mV', 'sample_rate': freq, 'physical_max': 1.0, 'physical_min': -2.0, 'digital_max': 8388607, 'digital_min': -8388608, 'prefilter': dict['prefilter'], 'transducer': dict['transducer']}
    
    logger.debug('Setting header for MMN channel %i...\n', x+1)
    m.setSignalHeader(x,mmn_chan_info)
    
    logger.debug('Organizing data for MMN channel %i to be properly written to output file...\n', x+1)
    mmn_chan_data.append(cropped_mmn.get_data(x))

logger.warning('Using pyedflib module, data dimensions for each channel header changed from "uV" to "mV"\n')  
    
logger.info('All MMN channel headers created\n')

logger.info('Writing MMN data to output MMN file...\n')
    
# Data padding added to end of MMN data to ensure all requested data points are in output data files.
logger.debug('Reorganizing and extending cropped MMN data to save into output file in proper format...\n')
mmn_data = []
for x in xrange(0,len(mmn_chan_data)):
    mmn_data.append(list(chain.from_iterable(mmn_chan_data[x])))
    tail_padding = numpy.repeat(mmn_data[x][-1],int(freq - (len(cropped_mmn) % freq)))
    mmn_data[x] = numpy.append(numpy.array(mmn_data[x]),tail_padding)

logger.debug('Writing data samples to MMN output file...\n')
for x in xrange(0,int(len(cropped_mmn)/freq)+1):
    for y in range (0, len(cropped_mmn.info['ch_names'])):
        m.writePhysicalSamples(mmn_data[y][x*int(freq):(x+1)*int(freq)])

logger.warning('Tail end of MMN data extended with extended data points, to ensure no MMN data is cut from final output\n')  
logger.info('Total real MMN data time = %s', len(cropped_mmn)/freq)
logger.info('Total MMN data time with data extension = %s\n', len(mmn_data[0])/freq)

logger.debug('Writing complete, closing file...\n')      
m.close()
logger.info('MMN data file complete!\n')


# Creates ABR .bdf data file from cropped ABR data using pyedflib module
logger.debug('Begin writing ABR data to .bdf file.\n')
a = pyedflib.EdfWriter(abr_outfile, len(cropped_abr.info['ch_names']), file_type=pyedflib.FILETYPE_BDF)

logger.info('Creating file: %s with %i channels.\n', abr_outfile, len(cropped_abr.info['ch_names']))

logger.debug('Writing input file header info into ABR header\n')
a.setHeader(header)

logger.info('Creating individual channel headers...\n')
x = 0
abr_chan_data = []

logger.debug('Writing individual channel headers in accordance to respective channels on input file...\n')
for x in xrange(0,len(cropped_abr.info['ch_names'])):
    dict = infile_info.getSignalHeader(x)
    abr_chan_info = {'label': dict['label'], 'dimension': 'mV', 'sample_rate': freq, 'physical_max': 1.0, 'physical_min': -2.0, 'digital_max': 8388607, 'digital_min': -8388608, 'prefilter': dict['prefilter'], 'transducer': dict['transducer']}
    
    # If not all channels are kept, indexing is not kept the same for event channel, so an excpetion has to be made to keep the event channel with a proper header
    if x == len(cropped_mmn.info['ch_names']):
        dict = infile_info.getSignalHeader(16)
        mmn_chan_info = {'label': dict['label'], 'dimension': 'mV', 'sample_rate': freq, 'physical_max': 1.0, 'physical_min': -2.0, 'digital_max': 8388607, 'digital_min': -8388608, 'prefilter': dict['prefilter'], 'transducer': dict['transducer']}

    logger.debug('Setting header for ABR channel %i...\n', x+1)
    a.setSignalHeader(x,abr_chan_info)
    
    logger.debug('Organizing data for ABR channel %i to be properly written to output file...\n', x+1)
    abr_chan_data.append(cropped_abr.get_data(x))

logger.warning('Using pyedflib module, data dimensions for each channel header changed from "uV" to "mV"\n')  
  
logger.info('All ABR channel headers created\n')

logger.info('Writing ABR data to output ABR file...\n')

# Data padding added to end of ABR data to ensure all requested data points are in output data files.
logger.debug('Reorganizing and extending cropped ABR data to save into output file in proper format...\n')
abr_data = []
for x in xrange(0,len(abr_chan_data)):
    abr_data.append(list(chain.from_iterable(abr_chan_data[x])))
    tail_padding = numpy.repeat(abr_data[x][-1],int(freq - (len(cropped_abr) % freq)))
    abr_data[x] = numpy.append(numpy.array(abr_data[x]),tail_padding)

logger.debug('Writing data samples to ABR output file...\n')
for x in xrange(0,int(len(cropped_abr)/freq)+1):
    for y in range (0, len(cropped_abr.info['ch_names'])):
        a.writePhysicalSamples(abr_data[y][x*int(freq):(x+1)*int(freq)])
        
logger.warning('Tail end of ABR data extended with extended data points, to ensure no ABR data is cut from final output\n')
logger.info('Total real ABR data time = %s', len(cropped_mmn)/freq)
logger.info('Total ABR data time with data extension = %s\n', len(abr_data[0])/freq)

logger.debug('Writing complete, closing file...\n')        
a.close()
logger.info('ABR data file complete!\n')

del infile_info

logger.info('File cropping complete! MMN and ABR .bdf files ready for use.\n')

# Allows user to view MMN and ABR data before program ends
logger.debug('Asking user if they would like to view MMN data plot...\n') 
logger.warning('Plotting all data info might take a while.')
view_mmn = raw_input("View MMN data plot? [y/n]: ")
while (len(view_mmn) >= 1):
    if view_mmn.upper() == 'Y':
        logger.debug('User indicated to view MMN data \n')
        mmn = mne.io.read_raw_edf(mmn_outfile, verbose = False)
        mmn.plot()
        break
    elif view_mmn.upper() == 'N': 
        logger.debug('User indicated not to view MMN data\n')
        break
    else:
        logger.debug('User entered an answer other than "Y" or "N", asked to re-enter a proper response\n')
        print("\nPlease enter a proper response.")
        view_mmn = raw_input("View MMN data plot? [y/n]: ")
        
logger.debug('Asking user if they would like to view ABR data plot...\n')
logger.warning('Plotting all data info might take a while.') 
view_abr = raw_input("View ABR data plot? [y/n]: ")
while (len(view_abr) >= 1):
    if view_abr.upper() == 'Y':
        logger.debug('User indicated to view ABR data \n')
        abr = mne.io.read_raw_edf(abr_outfile, verbose = False)
        abr.plot()
        break
    elif view_abr.upper() == 'N': 
        logger.debug('User indicated not to view ABR data\n')
        break
    else:
        logger.debug('User entered an answer other than "Y" or "N", asked to re-enter a proper response\n')
        print("\nPlease enter a proper response.")
        view_abr = raw_input("View ABR data plot? [y/n]: ")

logger.debug ('\n----------------------------------------END----------------------------------------\n')

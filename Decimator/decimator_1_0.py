# -*- coding: utf-8 -*-
#!/usr/bin/python

"""
File name: decimator.py
Author: Enrique Guzman
Date created: 01/25/2019
Date last modified: 02/04/2019
Version: 1.0.0
Credits: [Enrique Guzman, John V. Koger]
Copyright: 2019 Board of Regents of University of Wisconsin System

Description: Decimator takes in a raw .bdf EEG data file and returns a .bdf file with resampled and filtered data.

Arguments:
    --infile=[filename.bdf] or a complete file path (e.g Y:/study/year/folder/filename.bdf)     
    --outfile=[filename.bdf]   
    --mmn_pad=[#.##] (Default: 0.5 sec)  
    --abr_pad=[#.##] (Default: 0.1 sec)  
    --keep_all_channels (Default: keeps only first 6 EEG channels and the event channel)
    --samp_rate=[#] (Default if no arg: 512 Hz)   
    --low_freq=[#] (Default if no arg: None, no low freq cut-off)
    --high_freq=[#] (Default if no arg: 256, half of sampling rate)   
    --chans_to_filter=[#, #, #,...] (Default if no arg: None, all EEG channels filtered)
"""

import mne
import logging 
import sys
import os
import re
import pyedflib
import numpy
from itertools import chain

# Set up a logger to track progress of code
logger = logging.getLogger('Deci_Log')


# Ensures that certain information gets outputted to the user, while information needed for Debugging gets outputted to a log file. Log File created in script directory.
if not logger.handlers:
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('decimator.log', mode = 'w')
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

logger.info('\n   decimator.py\n   Version: 1.0.0\n   Created 2/4/2019\n   Copyright 2019 Board of Regents of University of Wisconsin System\n')

logger.info('Running File...\n')


# Measures how many arguments used when calling program, if none, throws error. If input and output filenames aren't called, error is thrown 
args = sys.argv
numargs = len(sys.argv) - 1     # -1 because [0] = self

logger.debug('Arguments read\n')
logger.info('%i arguments applied\n', numargs)

logger.debug('Checking if number of agruments called meets minimal requirement of input file and output file names (minimum number of arguments = 2)...\n')

if numargs == 0:
    logger.error('No arguments provided. Must at least provide input and output file names\n')
    logger.info('Possible arguments include:\n   --infile=[filename.bdf] or a complete file path (e.g Y:/study/year/folder/filename.bdf)\n   --outfile=[filename.bdf]\n   --samp_rate=[#] (Default if no arg: 512 Hz)\n   --low_freq=[#] (Default if no arg: None, no low freq cut-off)\n   --high_freq=[#] (Default if no arg: 256, half of sampling rate)\n   --chans_to_filter=[#] (Default if no arg: None, all EEG channels filtered)')
    sys.exit(0)
elif numargs < 2:
     logger.error('Not enough arguments provided. Must at least provide 1 input file and 1 output file names.\n')
     sys.exit(0)
     
     
# Checks for specific argument format. 1 input filename must be indicated in .bdf format, else error will be thrown, and 2 output file names must be indicated in .bdf format else error thrown (other arguments optional). 
infile = [s for s in args if 'infile' in s]
outfile = [s for s in args if 'outfile' in s]
bdf_files = [s for s in args if '.bdf' in s]

logger.debug('Checking if input and outfile arguments are in proper format (need 1 .bdf input file, and 2 .bdf output file names)...\n')

logger.debug('Looking for input file...\n')
if infile == []:
    logger.error('Input file name must be in proper format, please look above from proper argument format.\n')
    sys.exit(0)

if len(infile) != 1:
    logger.error('Please indicate only 1 input file name in .bdf format you wish to crop.\n')
    sys.exit(0)
   
logger.debug('Input file to crop found\n')

logger.debug('Looking for output file name...\n')
if outfile == []:
    logger.error('Output file name must be in proper format, please look above from proper argument format.\n')
    sys.exit(0)
    
if len(outfile) != 1:
    logger.error('Please indicate only 1 output file name in .bdf format.\n')
    sys.exit(0)
    
logger.debug('Output file name found\n')

if len(bdf_files) != 2:
    logger.error('Please indicate all file formats in .bdf format. 1 input file to crop, and 1 output file name to save decimated data to.\n')
    sys.exit(0)
    
logger.debug('Both files in .bdf format.\n')


# If only the 2 necessary arguments are called (input and output files), user is warned that all other values will be defaulted
if numargs == 3:
    logger.warning('Only input and output filenames included in arguments. samp_rate defaulted to 512 Hz, lowpass_freq defaulted to None, highpass_frew defaulted to 256, and all EEG channels in input file will be filtered\n')
    

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

logger.debug('\nAsking user if all inputted arguments are correct...\n') 
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
        
        
# Reads input file data and information
logger.info('Preparing file...\n')

logger.debug('Begin reading input file info\n')
raw = mne.io.read_raw_edf(fname, verbose = False)
print("\n")
logger.info('Input file overview: %s\n', raw)
freq = raw.info['sfreq']    #current sampling rate
logger.info('Loaded data sampling rate = %s Hz\n', freq)


# Identifies if user indicated specific desired sampling frequency. If no argument, Default value used samp_rate = 512 Hz.
logger.debug('Extracting desired sampling rate from arguments\n')
samp_rate = next((s for s in args if 'samp_rate' in s), None)

logger.debug('Finding new sampling rate...\n')
if samp_rate == None:
    sfreq = 512
    logger.debug('No samp_rate argument found, sfreq defaulted to 512 Hz\n')
else:
    sfreq = float(re.findall("\d+\.\d+", samp_rate)[0])
    logger.debug('Extracted sampling frequency = %s Hz\n', sfreq)
    
logger.info('Resampling frequency = %s Hz\n', sfreq)


# Identifies if user indicated specific low and highpass filter frequencies. If no argument, Default values used lowpass_freq = None and highpass_freq = sfreq/2 (half of new sampling rate)
logger.debug('Extracting low and high pass frequencies from arguments\n')
low = next((s for s in args if 'low_freq' in s), None)
high = next((s for s in args if 'high_freq' in s), None)

logger.debug('Finding low frequency cut-off\n')
if low == None:
    lfreq = None
    logger.debug('No low frequency cut-off argument found, low_freq defaulted to None\n')
else:
    lfreq = float(re.findall("\d+\.\d+", low)[0])
    logger.debug('Extracted low frequency cut-off = %s Hz\n', lfreq)
    
logger.info('Low frequency cut-off = %s Hz\n', lfreq)

logger.debug('Finding high frequency cut-off\n')
if high == None:
    hfreq = sfreq/2
    logger.debug('No high frequency cut-off argument found, high_freq defaulted to sfreq/2\n')
else:
    hfreq = float(re.findall("\d+\.\d+", high)[0])
    logger.debug('Extracted high frequency cut-off = %s Hz\n', hfreq)
    
logger.info('High frequency cut-off = %s Hz\n', hfreq)


# Loads file data in order to modify
logger.info('Data getting ready for modification...')
logger.debug('\nLoading all channel data for modification of channel data\n')
raw.load_data()
logger.debug('Data loaded.\n')


# Identifies if user indicated to filter only certain channels, if not, all EEG channels will be filtered
logger.debug('Checking if user indicated specific channels to filter\n')
chans = next((s for s in args if 'chans' in s),None)

logger.debug('Finding channels to filter\n')
if chans == None:
    picks = None
    logger.debug('No argument to filter specific channels found, all EEG channels will be filtered\n')
    logger.info('Filtering all EEG Channels...\n')
    
    filt_data = raw.filter(lfreq, hfreq, picks)
    """filt_datab = rawb.filter(lfreq, hfreq, picks)
    
    logger.debug('Combining the 2 MMN parts to save to output file...\n')
    filt_data.append(filt_datab)
    """
    logger.info('Filtered data ready for resampling.\n')

else:
    logger.debug('Argument specifying channels found\n')
    logger.info('Filtering specified channels...\n')
    
    picks = int(re.findall("\d+\.\d+", chans))
    filt_data = raw.filter(lfreq, hfreq, picks)
    logger.info('Filtered data ready for resampling\n')
    
    
# Resamples data to indicated sampling frequency, or if no argument, default resampling frequency = 512 Hz
logger.info('Resampling data from %s Hz to %s Hz...\n', freq, sfreq)
deci_data = filt_data.resample(sfreq)
logger.debug('Resampling complete\n')


# Gets output filename from called argument
logger.debug('Extracting output file name from arguments\n')
argout = next(s for s in args if 'outfile' in s)
outstring = argout.split('=')
deci_outfile = outstring[1]
logger.debug('Output file name found. File name = %s\n', deci_outfile)

logger.info('Saving output file data...\n')


# Gets input bdf file header from raw data file to use in the created decimated file
logger.debug('Reading input file header information to save into MMN and ABR files...\n')
infile_info = pyedflib.EdfReader(fname)


# Creates .bdf data file from decimated data using pyedflib module
logger.debug('Begin writing data to .bdf file.\n')
d = pyedflib.EdfWriter(deci_outfile, len(deci_data.info['ch_names']), file_type=pyedflib.FILETYPE_BDF)

logger.info('Creating file: %s with %i channels.\n', deci_outfile, len(deci_data.info['ch_names']))

logger.debug('Writing input file header info into decimated data header\n')
header = infile_info.getHeader()
d.setHeader(header)

logger.info('Creating individual channel headers...\n')
x = 0
chan_data = []

logger.debug('Writing individual channel headers in accordance to respective channels on input file...\n')
for x in xrange(0,len(deci_data.info['ch_names'])):
    dict = infile_info.getSignalHeader(x)
    chan_info = {'label': dict['label'], 'dimension': 'mV', 'sample_rate': sfreq, 'physical_max': 1.0, 'physical_min': -2.0, 'digital_max': 8388607, 'digital_min': -8388608, 'prefilter': dict['prefilter'], 'transducer': dict['transducer']}
    
    logger.debug('Setting header for channel %i...\n', x+1)
    d.setSignalHeader(x,chan_info)
    
    logger.debug('Organizing data for channel %i to be properly written to output file...\n', x+1)
    chan_data.append(deci_data.get_data(x))
    
logger.info('All channel headers created!\n')

logger.info('Writing data to output file...\n')

logger.debug('Reorganizing decimated channel data to save into output file in proper format...\n')


data = []
for x in xrange(0,len(chan_data)):
    data.append(list(chain.from_iterable(chan_data[x])))
    tail_padding = numpy.repeat(data[x][-1], 500)
    data[x] = numpy.array(data[x])

logger.debug('Writing data samples to output file...\n')
for x in xrange(0,int(len(deci_data)/sfreq)):
    for y in xrange (0, len(deci_data.info['ch_names'])):
        d.writePhysicalSamples(data[y][x*sfreq:(x+1)*sfreq])
        
logger.info('Total data runtime = %s\n', len(deci_data)/sfreq)
logger.debug('Writing complete, closing file...\n')      
d.close()
logger.info('MMN data file complete!\n')


# Allows user to view decimated data before program ends
logger.debug('Asking user if they would like to view decimated data plot...\n') 
logger.warning('Plotting all data info might take a while.')
view = raw_input("View decimated data plot? [y/n]: ")
while (len(view) >= 1):
    if view.upper() == 'Y':
        logger.debug('User indicated to view data \n')
        deci = mne.io.read_raw_edf(deci_outfile, verbose = False)
        deci.plot()
        break
    elif view.upper() == 'N': 
        logger.debug('User indicated not to view data\n')
        break
    else:
        logger.debug('User entered an answer other than "Y" or "N", asked to re-enter a proper response\n')
        print("\nPlease enter a proper response.")
        view = raw_input("View MMN data plot? [y/n]: ")
        
logger.debug ('\n----------------------------------------END----------------------------------------\n')


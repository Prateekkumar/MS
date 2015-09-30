# Module for generating data to be used in testing
"""
Publisher Toolbox Module
--------------------------------------------------------------------------

This module contains various functions in order to generate data
for comparisions for for publishers

__author__      = "Drew Garner"
__copyright__   = "Minesense"
"""
import os

def generate_cdfLog_hfems(output_filename="input.csv", 
                          repetitions=10,
                          HM=True,
                          HP=True,
                          numChannels=7,
                          numFreqs=14,
                          freqBase=100,
                          freqInterval=100,
                          ID=15,
                          dataInterval=1):

    oStr = ""
    outputFile = open(output_filename, 'w');
    base = "2015-09-13 11:18:19"

    print "Generating cdfPublisher Data: %s,\n repetitions: %d,\n HM: %r,\n HP: %r,\n Channels: %d,\n Freqs: %d,\n Base Freq: %d,\n Freq Interval: %d,\n ID: %d" % (os.path.abspath(output_filename), repetitions, HM, HP, numChannels, numFreqs, freqBase, freqInterval, ID)

    if(HM):
        oStr = "Date Time, SensorId, Timebase, HM, Channel"
        for freq in range(numFreqs):
            oStr = "%s, %d kHz"%(oStr, (freqBase + freq * freqInterval))
        oStr = "%s, Temperature, Calibration" % oStr
        outputFile.write("%s\n"%oStr) 
    if(HP):
        oStr = "Date Time, SensorId, Timebase, HP, Channel"
        for freq in range(numFreqs):
            oStr = "%s, %d kHz"%(oStr, (freqBase + freq * freqInterval))
        oStr = "%s, Temperature, Calibration" % oStr
        outputFile.write("%s\n"%oStr) 
    for rep in range(1,repetitions+1):
        if(HM):
            for channel in range(1, numChannels+1):
                oStr = "%s,%d,%d,HM,%d" % (base, ID, rep, channel)
                for freq in range(1,numFreqs+1):
                    oStr = "%s,%d"%(oStr, (channel + freq * 10 + rep * dataInterval))
                oStr = "%s,0,0" % oStr
                outputFile.write("%s\n"%oStr) 
        if(HP):
            for channel in range(1, numChannels+1):
                oStr = "%s,%d,%d,HP,%d" % (base, ID+1, rep, channel)
                for freq in range(1,numFreqs+1):
                    oStr = "%s,%d"%(oStr, (channel*-1 - freq * 10 - rep * dataInterval))
                oStr = "%s,0,0" % oStr
                outputFile.write("%s\n"%oStr) 

def generate_cdfLog_hfems_ones(output_filename="input.csv", 
                          repetitions=10,
                          HM=True,
                          HP=True,
                          numChannels=7,
                          numFreqs=14,
                          freqBase=100,
                          freqInterval=100,
                          ID=15,
                          runLength=5,
                          startVal=0):

    oStr = ""
    outputFile = open(output_filename, 'w');
    base = "2015-09-13 11:18:19"

    print "Generating cdfPublisher Data: %s,\n  repetitions: %d,\n  HM: %r,\n  HP: %r,\n  Channels: %d,\n  Freqs: %d,\n  Base Freq: %d,\n  Freq Interval: %d,\n  ID: %d\n  runLength: %d" % (os.path.abspath(output_filename), repetitions, HM, HP, numChannels, numFreqs, freqBase, freqInterval, ID, runLength)

    if(HM):
        oStr = "Date Time, SensorId, Timebase, HM, Channel"
        for freq in range(numFreqs):
            oStr = "%s, %d kHz"%(oStr, (freqBase + freq * freqInterval))
        oStr = "%s, Temperature, Calibration" % oStr
        outputFile.write("%s\n"%oStr) 
    if(HP):
        oStr = "Date Time, SensorId, Timebase, HP, Channel"
        for freq in range(numFreqs):
            oStr = "%s, %d kHz"%(oStr, (freqBase + freq * freqInterval))
        oStr = "%s, Temperature, Calibration" % oStr
        outputFile.write("%s\n"%oStr) 
    run = 0
    val = startVal
    for rep in range(1,repetitions+1):
        if(HM):
            for channel in range(1, numChannels+1):
                oStr = "%s,%d,%d,HM,%d" % (base, ID, rep, channel)
                for freq in range(1,numFreqs+1):
                    oStr = "%s,%d"%(oStr, val)
                oStr = "%s,0,0" % oStr
                outputFile.write("%s\n"%oStr) 
        if(HP):
            for channel in range(1, numChannels+1):
                oStr = "%s,%d,%d,HP,%d" % (base, ID+1, rep, channel)
                for freq in range(1,numFreqs+1):
                    oStr = "%s,%d"%(oStr, val)
                oStr = "%s,0,0" % oStr
                outputFile.write("%s\n"%oStr)
        run = run + 1
        if(run >= runLength):
            if val == 0:
                val = 1
            else:
                val = 0
            run = 0

if __name__=="__main__":
    generate_cdfLog_hfems(output_filename="alt.csv", HP=False)

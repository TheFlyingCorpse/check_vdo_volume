#!/usr/bin/env python3
import subprocess
import traceback
import sys
import argparse

#######################################
# Written by Rune Darrud - 2020-07-01 #
# Version 0.1                         #
#######################################

returncode = 3
outputSummary = ""
perfdata = list()
output = list()
vdoStats = dict()

try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--volume", help="VDO Volume to check")
        parser.add_argument("--warning", default=80, type=int, help="Percent used warning")
        parser.add_argument("--critical", default=90, type=int, help="Percent used critical")
        args = parser.parse_args()
        volume = args.volume
        warning = args.warning
        critical = args.critical

        vdoStatsOutput = str(subprocess.check_output(['vdostats','--verbose',volume], stderr=subprocess.DEVNULL).decode()).split('\n')

        desiredOutputList = ['data blocks used','overhead blocks used','logical blocks used','physical blocks','logical blocks','block size',
                'used percent','saving percent','operating mode','current VDO IO requests in progress','maximum VDO IO requests in progress']

        for entry in vdoStatsOutput:
                if entry.startswith(volume):
                        continue
                tempEntry = entry.strip().split(':')
                if len(tempEntry) > 1:
                        key = tempEntry[0].strip()
                        val = tempEntry[1].strip()
                        if key in desiredOutputList:
                          vdoStats[key] = val

        # Calculate the blocks to bytes in the perfdata output
        blocksize = int(vdoStats['block size'])
        perfdata.append('logical space used bytes=' + str(int(vdoStats['logical blocks used']) * blocksize) + 'b;;;0;' + str(int(vdoStats['logical blocks']) * blocksize))
        perfdata.append('data space used bytes=' + str(int(vdoStats['data blocks used']) * blocksize) + 'b;;;0;')
        perfdata.append('overhead space used=' + str(int(vdoStats['overhead blocks used'])* blocksize)  + 'b;;;0;')

        perfdata.append('data blocks used=' + str(vdoStats['data blocks used']) + ';;;0;')
        perfdata.append('overhead blocks used=' + str(vdoStats['overhead blocks used']) + ';;;0;')
        perfdata.append('logical blocks used=' + str(vdoStats['logical blocks used']) + ';;;0;' + str(vdoStats['logical blocks']))

        perfdata.append('used percent=' + str(vdoStats['used percent']) + '%;' + str(warning) + ';' + str(critical) + ';0;100')
        perfdata.append('saving percent=' + str(vdoStats['saving percent']) + '%;;;0;100')
        perfdata.append('current VDO IO requests in progress=' + str(vdoStats['current VDO IO requests in progress']) + ';;;0;' + str(vdoStats['maximum VDO IO requests in progress']))

        usedPercent = int(vdoStats['used percent'])
        operatingMode = vdoStats['operating mode']
        # normal mode and used is less than warning
        if operatingMode == 'normal' and usedPercent < warning:
                returncode = 0
                outputSummary = 'The VDO volume \'' + volume + '\' is ok'
                output.append('Currently used \'' + str(usedPercent) + '%\'')
                output.append('The operating mode is \'' + str(operatingMode) + '\'')
        # Thresholds passed
        elif operatingMode == 'normal':
        # Operatingmode is not normal
                if usedPercent > critical:
                        returncode = 2
                        outputSummary = 'Used is above the critical mark for volume \'' + str(volume) + '\''
                else:
                        returncode = 1
                        outputSummary = 'Used is above the warning mark for volume \'' + str(volume) + '\''

                output.append('The operating mode is \'' + str(operatingMode) + '\'')
        else:
                returncode = 3
                outputSummary = 'The VDO volume \'' + volume + '\' is currently \'' + str(operatingMode) + '\''

except:
        print('UNKOWN ERROR:')
        traceback.print_exc(file=sys.stdout)
        sys.exit(returncode)
finally:
        if returncode == 3:
                print('[UNKNOWN] ' + outputSummary)
        elif returncode == 2:
                print('[CRITICAL] ' + outputSummary)
        elif returncode == 1:
                print('[WARNING] ' + outputSummary)
        elif returncode == 0:
                print('[OK] ' + outputSummary)

        print('\n'.join(output) + ' | ' + ' '.join(perfdata))
        sys.exit(returncode)

from __future__ import print_function
import os
import argparse
import numpy as np
from itertools import repeat
import pandas as pd
from lsst.sims.movingObjects import Orbits
from lsst.sims.movingObjects import PyOrbEphemerides


# Simple script to generate an ephemeris at a user-specified (UTC) time.

if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Python script to generate ephemerides using oorb')
    parser.add_argument('--orbitFile', type=str, default=None, help='Input orbit file (.des COMETARY format)')
    parser.add_argument('--obsCode', type=str, default='I33', help='Observatory code for ephemerides')
    parser.add_argument('--ephTimesFile', type=str, default=None, help='Filename containing MJD-UTC times for ephemerides')
    parser.add_argument('--ephTimes', type=str, default=None, help='List of MJD-UTC times for ephemerides (if >1: in quotes, separated by spaces')
    parser.add_argument('--diasources', type=bool, default=False, help='Save output as MOPS diasource type file')
    parser.set_defaults()
    args = parser.parse_args()


    # Read orbits.
    orbits = Orbits()
    orbits.readOrbits(args.orbitFile)

    # Set up ephemeris generation.
    pyephems = PyOrbEphemerides()
    pyephems.setOrbits(orbits)

    # set observatory code
    obscode = args.obsCode

    # Set up dates to predict ephemerides.
    if args.ephTimes is not None:
        times = np.array(args.ephTimes.split(), float)
        obshistids = np.arange(0, len(times))

    elif args.ephTimesFile is not None:
        times = pd.read_table(args.ephTimesFile, delim_whitespace=True, names=['MJD-UTC'])
        times = times['MJD-UTC'].as_matrix()

    else:
        raise Exception('Did not have any ephemeride times')

    #print("Using times: ", times)

    # Generate ephemerides.
    ephs = pyephems.generateEphemerides(times, obscode=obscode, timeScale='UTC', byObject=True)

    # print results as diasources?
    if args.diasources==True:
        print('DiaID ObshistId ObjID MJD(UTC)    RA    Dec   MJD_UTC MagV FakeSNR')
        diacounter = 0
        obshistids = np.arange(0, len(times))
        for j, o in orbits.orbits.iterrows():
            for i, obshist in enumerate(obshistids):
                print(diacounter, obshist, o.objId, ephs['ra'][j][i], ephs['dec'][j][i], ephs['time'][j][i], ephs['magV'][j][i], 5)
                diacounter += 1

    else:
        print('ObjId MJD(UTC) RA Dec dRAdt dDecdt Delta magV Elongation')
        for e, o in zip(ephs, orbits):
            for i in range(len(e)):
                print(o.orbits.objId.iloc[0], e['time'][i], e['ra'][i], e['dec'][i], e['dradt'][i], e['ddecdt'][i],\
                    e['delta'][i], e['magV'][i], e['solarelon'][i])

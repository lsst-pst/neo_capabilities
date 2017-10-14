# Set up basics.
import os
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import pandas as pd
# Set up MAF
import lsst.sims.maf.metrics as metrics
import lsst.sims.maf.slicers as slicers
import lsst.sims.maf.plots as plots
import lsst.sims.maf.db as db
import lsst.sims.maf.metricBundles as mmb
import lsst.sims.maf.utils as utils

import sys
try:
    # remove a conflict on my personal system
    sys.path.remove('/Users/lynnej/work/lsst')
except ValueError:
    pass
sys.path.append(os.path.join(os.getenv('SIMS_MAF_DIR'), 'bin.src'))
import movingObjects as moO


doPHA = True
doNEO = False

orbitFile = {}
orbitFile['pha'] = 'orbits/pha_5k'
orbitFile['neo'] = 'orbits/neo_5k'


Hmark = 22
Hrange = np.arange(11, 28.5, 0.5)
Hidx = np.where(Hrange == 22)[0]
outDir = 'other_telescopes'
if not (os.path.isdir(outDir)):
    os.makedirs(outDir)


ephemFile = {}
ddir = '/Users/lynnej/otherRepos/neo_capabilities/data'
ephemFile['pha'] = os.path.join(ddir, 'daily_pha_5k')  # PHA ephems from 2000-2034
ephemFile['neo'] = os.path.join(ddir, 'daily_neo_5k')  # NEO ephems from 2000-2034

runNow = []
if doPHA:
    runNow.append('pha')
if doNEO:
    runNow.append('neo')

ephems = {}
for t in runNow:
    ephems[t] = pd.read_table(ephemFile[t], delim_whitespace=True)

# Add some columns to the ephem file - these are used to calculate appMagV.
def add_velocity(ephs):
    ephs['velocity'] = np.sqrt(ephs['dRAdt']**2 + ephs['dDecdt']**2)
    return ephs

def calcMagLosses(ephs, seeing=0.75, texp=30.):
    """
    Calculate the magnitude losses due to trailing and not matching the point-source detection filter.
    """
    a_trail = 0.76
    b_trail = 1.16
    a_det = 0.42
    b_det = 0.00
    x = ephs['velocity'] * texp / seeing / 24.0
    ephs['dmagTrail'] = 1.25 * np.log10(1 + a_trail*x**2/(1+b_trail*x))
    ephs['dmagDetect'] = 1.25 * np.log10(1 + a_det*x**2 / (1+b_det*x))
    return ephs

# Add some more 'dummy' columns to ephem file - these just need to be there for SNR/vis/magFilter calculation, but
# we won't use them for peakV / known object calculation.
def add_dummycols(ephs):
    ephs['magFilter'] = ephs['magV']
    ephs['fiveSigmaDepth'] = np.ones(len(ephs), float) * 28.0
    return ephs


for t in runNow:
    ephems[t] = add_velocity(ephems[t])
    ephems[t] = calcMagLosses(ephems[t])
    ephems[t] = add_dummycols(ephems[t])
    cols = ephems[t].columns.values
    cols[0] = 'objId'
    ephems[t].columns = cols


# Set up the moving object slicers for each of these ephemeride files.
slicerEphs =  {}
for t in runNow:
    slicerEphs[t] = moO.setupSlicer(orbitFile[t], Hrange, obsFile=None)
    slicerEphs[t].obs = ephems[t]
    slicerEphs[t].allObs = ephems[t]
    slicerEphs[t].obsfile = ephemFile[t]

# And set up the moving object metricBundles.
plotFuncs = [plots.MetricVsH()]

knownBundle0 = {}
knownBundle1 = {}
knownBundle2 = {}
knownBundle3 = {}
peakVBundle = {}
for t in runNow:
    plotDict = {'nxbins': 200, 'nybins': 200,
                'title': '%s: %s' % ("Previously known", t)}

    metric = metrics.KnownObjectsMetric(vMagThresh1=20.0, eff1=0.05, tSwitch1=53371,
                                        vMagThresh2=21.0, eff2=0.05, tSwitch2=57023,
                                        vMagThresh3=22.0, eff3=0.05, tSwitch3=59580,
                                        vMagThresh4=22.0, eff4=0.10, elongThresh=60)
    knownBundle0[t] = mmb.MoMetricBundle(metric, slicerEphs[t], None,
                                        runName="Previously known 0", metadata=t,
                                        plotDict=plotDict, plotFuncs=plotFuncs)
    metric = metrics.KnownObjectsMetric(vMagThresh1=20.0, eff1=0.05, tSwitch1=53371,
                                        vMagThresh2=21.0, eff2=0.05, tSwitch2=57023,
                                        vMagThresh3=22.0, eff3=0.05, tSwitch3=59580,
                                        vMagThresh4=22.0, eff4=0.10, elongThresh=100)
    knownBundle1[t] = mmb.MoMetricBundle(metric, slicerEphs[t], None,
                                        runName="Previously known 1", metadata=t,
                                        plotDict=plotDict, plotFuncs=plotFuncs)
    metric = metrics.KnownObjectsMetric(vMagThresh1=20.0, eff1=0.05, tSwitch1=53371,
                                        vMagThresh2=21.0, eff2=0.05, tSwitch2=57023,
                                        vMagThresh3=22.0, eff3=0.05, tSwitch3=59580,
                                        vMagThresh4=22.2, eff4=0.10, elongThresh=100)
    knownBundle2[t] = mmb.MoMetricBundle(metric, slicerEphs[t], None,
                                        runName="Previously known 2", metadata=t,
                                        plotDict=plotDict, plotFuncs=plotFuncs)
    metric = metrics.KnownObjectsMetric(vMagThresh1=20.0, eff1=0.05, tSwitch1=53371,
                                        vMagThresh2=21.0, eff2=0.05, tSwitch2=57023,
                                        vMagThresh3=22.0, eff3=0.05, tSwitch3=59580,
                                        vMagThresh4=22.2, eff4=0.20, elongThresh=100)
    knownBundle3[t] = mmb.MoMetricBundle(metric, slicerEphs[t], None,
                                        runName="Previously known 3", metadata=t,
                                        plotDict=plotDict, plotFuncs=plotFuncs)
    metric = metrics.PeakVMagMetric()
    peakVBundle[t] = mmb.MoMetricBundle(metric, slicerEphs[t], None,
                                        runName="PeakVMag", metadata=t, plotDict=plotDict, plotFuncs=plotFuncs)


# Calculate  the peak V magnitude and times of 'discovery' (passing mag threshhold) for each object
for t in runNow:
    bg = mmb.MoMetricBundleGroup({0:knownBundle0[t], 1:knownBundle1[t], 2:knownBundle2[t],
                                  3:knownBundle3[t], 4: peakVBundle[t]},
                                 outDir=outDir, resultsDb=None)
    bg.runAll()


times = np.arange(knownBundle0[runNow[0]].slicer.obs['MJD(UTC)'].min(),
                  knownBundle0[runNow[0]].slicer.obs['MJD(UTC)'].max() + 1, 30)
summaryMetric = metrics.MoCompletenessAtTimeMetric(times=times, Hindex=0.33, Hval=22)

for t in runNow:
    knownBundle0[t].setSummaryMetrics(summaryMetric)
    knownBundle0[t].computeSummaryStats()
    knownBundle1[t].setSummaryMetrics(summaryMetric)
    knownBundle1[t].computeSummaryStats()
    knownBundle2[t].setSummaryMetrics(summaryMetric)
    knownBundle2[t].computeSummaryStats()
    knownBundle3[t].setSummaryMetrics(summaryMetric)
    knownBundle3[t].computeSummaryStats()

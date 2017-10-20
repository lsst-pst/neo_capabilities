from __future__ import print_function
import os, sys
from glob import glob
import numpy as np

import lsst.sims.maf.metricBundles as mb
import lsst.sims.maf.plots as plots
import lsst.sims.maf.metrics as metrics
import lsst.sims.maf.slicers as slicers

runname = sys.argv[1]
obj = sys.argv[2]
ddir = os.path.join('.',  runname + '_' + obj)
orbitFile = 'orbits/%s_5k' % obj

Hval = 22

strategy = ['3 pairs in 12 nights', '3 pairs in 15 nights', '3 pairs in 20 nights', 
            '3 pairs in 25 nights', '3 pairs in 30 nights', '4 pairs in 20 nights']
strategy += ['3 pairs in 15 nights SNReq4', '3 pairs in 30 nights SNReq4']
strategy += ['3 pairs in 15 nights SNReq0']
strategy += ['Single detection', 'Single pair']
strategy += ['6 detections in 60 nights']
#strategy += ['3 pairs in 15 nights trailing loss', '3 pairs in 30 nights trailing loss']
#strategy += ['3 pairs in 15 nights trailing loss SNReq4', '3 pairs in 30 nights trailing loss SNReq4']
#strategy += ['3 pairs in 15 nights SNReq5detection loss', '3 pairs in 15 nights SNReq5trailing loss']
#strategy += ['3 pairs in 30 nights SNReq5detection loss', '3 pairs in 30 nights SNReq5trailing loss']
strategy = [s + ' trailing loss' for s in strategy]

times = np.arange(59579, 65055.15+5, 10)
summaryMetricsT = [metrics.MoCompletenessAtTimeMetric(times=times, Hval=22,cumulative=False, Hindex=0.33),
                  metrics.MoCompletenessAtTimeMetric(times=times, Hval=22, cumulative=True, Hindex=0.33)]
summaryMetricsH = [metrics.MoCompletenessMetric(cumulative=False, Hindex=0.33),
                  metrics.MoCompletenessMetric(cumulative=True, Hindex=0.33)]


bundle = {}
foundstrat = []
for strat in strategy:
    pattern = os.path.join(ddir, runname + '*' + strat.replace(' ', '_') + '_MOOB.h5')
    match = glob(pattern)
    filename = None
    for m in match:
        if 'Discovery' in m:
            if ('Time' in m) or ('N_chances' in m) or ('Magic' in m):
                filename = m
    if filename is None:
        print('Could not find metric file for %s (%s)' % (strat, pattern))
        continue
    foundstrat.append(strat)
    bundle[strat] = mb.createEmptyMoMetricBundle()
    bundle[strat].read(filename)
    if 'Time' in bundle[strat].fileRoot:
        bundle[strat].setSummaryMetrics(summaryMetricsT)
    else:
        bundle[strat].setSummaryMetrics(summaryMetricsH)
    bundle[strat].computeSummaryStats()

strategy = foundstrat
strat = foundstrat[0]
# old runs : 59580 start 
# v4 runs: 59853 start
#10 years, old runs
diff = np.abs(times-(63230.50 + 0))
yr10idx = np.where(diff == np.min(diff))[0]
#12 years, old runs
diff = np.abs(times-(63960 + 0))
yr12idx = np.where(diff == np.min(diff))[0]
print("year 10", yr10idx, times[yr10idx], "year 12", yr12idx, times[yr12idx])

for indx  in [yr10idx, yr12idx]:
    print('TIME:', times[indx])
    print(runname, obj)
    Hidx = np.where(np.abs(bundle[strat].slicer.Hrange - Hval) == np.abs(bundle[strat].slicer.Hrange - Hval).min())  
    print('H range stepsize', np.diff(bundle[strat].slicer.Hrange).mean(), 'Hval', bundle[strat].slicer.Hrange[Hidx])
    print("Cumulative")
    for strat in strategy:
        Hidx = np.where(np.abs(bundle[strat].slicer.Hrange - Hval) == np.abs(bundle[strat].slicer.Hrange - Hval).min())  
        try:
            print(strat, bundle[strat].summaryValues['CumulativeCompleteness@Time']['name'][indx],
                  bundle[strat].summaryValues['CumulativeCompleteness@Time']['value'][indx])
        except KeyError:
            try:
                print(strat, bundle[strat].summaryValues['CumulativeCompleteness']['name'][Hidx],
                      bundle[strat].summaryValues['CumulativeCompleteness']['value'][Hidx])
            except KeyError:
                print(strat, 'N/A')
    print("Differential")
    for strat in strategy:
        Hidx = np.where(np.abs(bundle[strat].slicer.Hrange - Hval) == np.abs(bundle[strat].slicer.Hrange - Hval).min())
        try:
            print(strat, bundle[strat].summaryValues['DifferentialCompleteness@Time']['name'][indx],
                  bundle[strat].summaryValues['DifferentialCompleteness@Time']['value'][indx])
        except KeyError:
            try:
                print(strat, bundle[strat].summaryValues['DifferentialCompleteness']['name'][Hidx],
                      bundle[strat].summaryValues['DifferentialCompleteness']['value'][Hidx])
            except KeyError:
                print(strat, 'N/A')

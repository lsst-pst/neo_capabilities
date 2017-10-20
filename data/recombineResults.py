from __future__ import print_function
import os
from glob import glob
import numpy as np
import numpy.ma as ma
import pandas as pd
import matplotlib.pyplot as plt

import lsst.sims.maf.metricBundles as mb
import lsst.sims.maf.plots as plots
import lsst.sims.maf.metrics as metrics
import lsst.sims.maf.slicers as slicers

import sys
#sys.path.append(os.path.join(os.getenv('SIMS_MAF_DIR'), 'bin.src'))
#import movingObjects as moO

runname = sys.argv[1]
print('Working on run %s' % runname)

for t in ('pha', 'neo'):
    tf = t + '_5k'
    ddir = os.path.join('%s_split_res_2' % (t), runname)
    outdir = '%s_%s' % (runname, t)
    if not (os.path.isdir(outdir)):
        os.makedirs(outdir)
    orbitFile = os.path.join('orbits', '%s' % tf)

    slicer = slicers.MoObjSlicer()
    Hrange1 = np.arange(14, 28., 0.2)
    slicer.readOrbits(orbitFile, Hrange=Hrange1)

    splits = os.listdir(os.path.join('orbits', '%s_split' % t))
    print('orbit files', splits)

    filenames = glob(os.path.join(ddir, '%s*%s_00_*h5' % (runname, tf)))
    print('ddir', ddir)

    for f in filenames:
        print('File', f)
        bundles = {}
        froot = os.path.basename(f)
        strategy = froot.replace(runname, '').replace('%s_00' % tf, '').replace('_MOOB.h5', '').replace('_', ' ')
        strategy.lstrip(' ').rstrip(' ')
        print('Detection strategy', strategy)
        for spl in splits:
            bundles[spl] = mb.createEmptyMoMetricBundle()
            f_spl = froot.replace('%s_00' % tf, '%s' % spl)
            bundles[spl].read(os.path.join(ddir, f_spl))
            Hrange = bundles[spl].slicer.Hrange
            if spl.endswith('_00'):
                Hrange1 = Hrange
            if np.any(Hrange != Hrange1):
                raise ValueError('Hrange not matching, %s %s' % (f, spl))
            bundles[spl].slicer = slicer
        jbundle = mb.createEmptyMoMetricBundle()
        jbundle.read(f)
        jbundle.slicer = slicer
        jbundle.slicer.Hrange = Hrange1
        mvals = np.zeros((len(slicer.orbits), len(Hrange1)), float)
        mvalsMask = np.ones((len(slicer.orbits), len(Hrange1)), dtype=bool)
        for spl in splits:
            if np.any(np.not_equal(bundles[spl].slicer.Hrange, Hrange1)):
                raise ValueError('Incompatible results, Hrange varies')
            try:
                mvals = mvals + bundles[spl].metricValues.filled(0)
            except:
                print('Skipping %s' % f)
                break
            mvalsMask = np.where(mvalsMask & bundles[spl].metricValues.mask, True, False)
        jbundle.metricValues = ma.MaskedArray(data=mvals, mask=mvalsMask, fill_value=0)
        jbundle.metadata = '%s ' % t.upper() + strategy
        jbundle.runname = runname
        jbundle.fileRoot = froot.replace('%s_00' %tf, tf).replace('.h5', '')
        jbundle.write(outDir=outdir)


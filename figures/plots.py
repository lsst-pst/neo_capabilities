import numpy as np
import matplotlib.pyplot as plt
import itertools

figformat = 'pdf'

def make_orbit_plot(orbitFile='pha20141031.des'):
    from lsst.sims.movingObjects import Orbits
    o = Orbits()
    o.readOrbits(orbitFile)
    o.orbits['a'] = o.orbits['q'] / (1 - o.orbits['e'])
    plt.figure(figsize=(8,8))
    ax1 = plt.subplot(2, 1, 1)
    plt.plot(o.orbits['a'], o.orbits['e'], 'o', markersize=4, alpha=0.7)
    plt.xlim(0, 4)
    plt.ylim(0, 1)
    q = 1.05
    a = np.arange(0, 5, .05)
    e = 1 - q/a
    plt.plot(a, e, 'k:')
    Q = 0.95
    e = Q/a - 1
    plt.plot(a, e, 'k:')
    plt.ylabel(r'Eccentricity')
    if orbitFile.startswith('pha'):
        plt.title('PHA orbital distribution', fontsize='larger')
    else:
        plt.title('NEO orbital distribution', fontsize='larger')
    plt.subplot(2, 1, 2, sharex=ax1)
    plt.plot(o.orbits['a'], o.orbits['inc'], 'o', markersize=4, alpha=0.7)
    plt.xlim(0, 5)
    plt.xlabel(r'Semi-major Axis (AU)')
    plt.ylabel(r'Inclination ($^\circ$)')
    plt.savefig('%s_orbits.' % orbitFile.rstrip('.des') + figformat, format=figformat)


def make_fov_plot(calcFill=False):
    # For the footprint generation.
    import lsst.sims.utils as sims_utils
    from lsst.obs.lsstSim import LsstSimMapper
    from lsst.sims.coordUtils import chipNameFromPupilCoords
    from lsst.sims.coordUtils import getCornerPixels, getCornerRaDec
    from lsst.afw.cameraGeom import SCIENCE

    mapper = LsstSimMapper()
    camera = mapper.camera
    obs = ObservationMetaData(pointingRA=0.0, pointingDec=0.0, rotSkyPos=0.0, mjd=59580.0)

    if calcFill:
        # Set up pupil coordinate points to iterate over (to calculate fill factor)
        testrange = 2.2
        spacing = 0.01
        xcen = 0
        ycen = 0
        xi = np.arange(xcen-np.radians(testrange), xcen+np.radians(testrange), np.radians(spacing))
        yi = np.arange(ycen-np.radians(testrange), ycen+np.radians(testrange), np.radians(spacing))
        x = []
        y = []
        for i in itertools.product(xi, yi):
            x.append(i[0])
            y.append(i[1])
        x = np.array(x)
        y = np.array(y)

        # Calculate 'visibility'
        chipNames = chipNameFromPupilCoords(x, y, camera=camera)
        vis = np.zeros(len(chipNames))
        for i, chip in enumerate(chipNames):
            if chip is not None:
                vis[i] = 1

        # Calculate fill factor
        area_degsq = 9.6
        innerradius = 1.75
        print 'inner radius matching area_degsq for circle', innerradius
        sep = np.degrees(sims_utils.haversine(x, y, xcen, ycen))
        print 'max distance from center used for chip calculation', sep.max()
        incircle = np.where(sep < innerradius)[0]
        onchip = np.where(vis[incircle] == 1)[0]
        fillfactor = len(vis[onchip]) / float(len(vis[incircle]))
        print 'fill factor', fillfactor
        innerfillfactor = fillfactor
        outerradius = 2.06
        print 'outer radius', outerradius
        sep = np.degrees(sims_utils.haversine(x, y, xcen, ycen))
        print 'max distance from center used for chip calculation', sep.max()
        incircle = np.where(sep < outerradius)[0]
        onchip = np.where(vis[incircle] == 1)[0]
        fillfactor = len(vis[onchip]) / float(len(vis[incircle]))
        print 'fill factor', fillfactor
    else:
        innerradius = 1.75
        outerradius = 2.06
        innerffillfactor = 0.895

    # Build locations of CCD corners.
    ccdnames = []
    for det in camera:
        if det.getType() == SCIENCE:
            ccdnames.append(det.getName())
    corners = []
    for ccdname in ccdnames:
        corners.append(np.radians(getCornerRaDec(ccdname, camera, obs_metadata=obs)))

    plt.figure(figsize=(8, 6))
    plt.axis('equal')
    #condition = np.where(vis == 1)[0]
    #plt.plot(np.degrees(x), np.degrees(y), 'g.', markersize=0.2)
    #plt.plot(np.degrees(x[condition]), np.degrees(y[condition]), 'b.', markersize=0.3)
    for cornerset in corners:
        cx = corners.swapaxes(0, 1)[0]
        cy = corners.swapaxes(0, 1)[1]

    plt.plot(0, 0, 'r.')
    plt.xlabel('x Pupil (deg)', fontsize='larger')
    plt.ylabel('y Pupil (deg))', fontsize='larger')
    theta = np.arange(0, 2*np.pi, 0.01)
    plt.plot(innerradius*np.cos(theta)+np.degrees(xcen), innerradius*np.sin(theta)+np.degrees(ycen), 'r-')
    plt.plot(outerradius*np.cos(theta)+np.degrees(xcen), outerradius*np.sin(theta)+np.degrees(ycen), 'r:')
    #plt.xlim(fieldra+offset-sep.max()/2.0, fieldra+offset+sep.max()/2.0)
    plt.ylim(np.degrees(xcen)-sep.max()*.7, np.degrees(ycen)+sep.max()*.7)
    xco = 0.74
    plt.figtext(xco, 0.8, 'Inner circle')
    plt.figtext(xco, 0.75, r' r=%.2f$^\circ$' %(innerradius))
    plt.figtext(xco, 0.7, ' %.0f%s fill factor' %(round(innerfillfactor*100), '%'))
    plt.figtext(xco, 0.6, 'Outer circle')
    plt.figtext(xco, 0.55, r' r=%.2f$^\circ$' %(outerradius))
    plt.savefig('focalplane.' + figformat, format=figformat)




if __name__ == '__main__':
    # Plot orbital elements.
    #make_orbit_plot('pha20141031.des')
    make_orbit_plot('phas_2k.des')
    make_orbit_plot('neos_2k.des')

    # Make fov plot.
    #make_fov_plot()

    # Make opsim footprints - use plot_footprint.py (from sims_operations/tools)

    plt.show()

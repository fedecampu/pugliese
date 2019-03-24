import sys
import numpy as np
from astropy.io import fits
from sklearn.externals import joblib


def get_orders(wavelength):

    diff = np.abs(np.diff(wavelength))
    idx = np.argwhere(diff > 0.1)
    idx = np.insert(idx, 0, 0)
    idx = np.insert(idx, len(idx), -1)

    return wavelength[idx]


def find_order(wavelength, order_list, n_order):

    idx1 = np.where(np.isclose(order_list[n_order], wavelength))[0][0]
    idx2 = np.where(np.isclose(order_list[n_order+1], wavelength))[0][0]

    return slice(idx1+3, idx2)


#%% Read FITS files.
file1 = sys.argv[1]
file2 = sys.argv[2]

fits1 = fits.open(file1)
data1 = fits1[0].data
wavel1 = data1[7]
spec1 = data1[8]

fits2 = fits.open(file2)
header2 = fits2[0].header
data2 = fits2[0].data
wavel2 = data2[7]
spec2 = data2[8]
airmass2 = float(header2['AIRMASS'])
exptime2 = float(header2['EXPTIME'])


#%% Search orders.
orders = get_orders(wavel1)

reference = []
for i in range(len(orders)-1):

    l1 = find_order(wavel1, orders, i)
    reference.append((wavel1[l1], spec1[l1]))


#%% Wavelength calibration.
fixed = []
for i in range(len(orders)-1):

    l1 = find_order(wavel1, orders, i)
    l2 = find_order(wavel2, orders, i)

    iflux = np.interp(wavel1[l1], wavel2[l2], spec2[l2])
    fixed.append((wavel1[l1], iflux))


#%% Extinction correction.
mags = []
for i in range(len(fixed)):
    mag = (-2.5)*np.log10(fixed[i][1])
    mags.append(mag)

mags_mean = mags[:]
for i in range(len(mags_mean)):
    mean = np.nanmean(mags[i])
    mask_nan = np.isnan(mags[i])
    mags_mean[i] = np.copy(mags[i])
    mags_mean[i][mask_nan] = mean


ext = np.array([[3.10e+02, 1.37e+00],
                [3.20e+02, 8.20e-01],
                [3.40e+02, 5.10e-01],
                [3.60e+02, 3.70e-01],
                [3.80e+02, 3.00e-01],
                [4.00e+02, 2.50e-01],
                [4.50e+02, 1.70e-01],
                [5.00e+02, 1.30e-01],
                [5.50e+02, 1.20e-01],
                [6.00e+02, 1.10e-01],
                [6.50e+02, 1.10e-01],
                [7.00e+02, 1.00e-01],
                [8.00e+02, 7.00e-02],
                [9.00e+02, 5.00e-02]])

iext = []
for i in range(len(reference)):

    wav_ext = ext[:,0]
    val_ext = ext[:,1]
    iext.append(np.interp(reference[i][0], wav_ext, val_ext, left=0., right=0.))

corr = []
for i in range(len(iext)):
    corr.append(iext[i]*airmass2)

mags_corr = []
for i in range(len(mags_mean)):
    mags_corr.append(mags_mean[i] - corr[i])

flux_corr = []
for i in range(len(mags_corr)):
    flux_corr.append(np.power(10, -1*mags_corr[i]/2.5)/exptime2)


#%% Writing binary output.
for i in range(len(fixed)):
    fixed[i] = (fixed[i][0], flux_corr[i])

joblib.dump(fixed, file2.replace('.fits', '.joblib'))

#                                           #
#                                           #
#       PUGLIESE - TANGO TO USE OPERA       #
#                                           #
#                                           #

This program works to complete the flux calibration of OPERA Reduction.

TO RUN:

>> source pugliese.sh


IMPORTANT:

To do a program usable, you MUST indicate:

 1 - Ref standard observation to do the interpolation between science and standard observations.
    
    1 - a:  in pugliese.sh, must indicate the REF standard.

        FOR EXAMPLE: 
                    line 1: 
                                    REF='./standard/N20180423G0057i.fits'


 2 - Indicate the localization of the science files. In case that you have differents runs on observations, you MUST define different directories, and must change in two lines:
                   
    2 - a : in "pugliese.sh": 

        FOR EXAMPLE: 
                    line 5:
                                    LIST=$(ls ./{standard,science1}/*.fits)

    2 - b : in "pugliese_norm.py":
                             line 38:
                                    jobsci = sorted(glob('./science1/*.joblib'))

here you will indicate the directory where are the .joblib files.


 3 - Indicate the ORDER of the poly fit to the standard flux calibration.

    3 - a: in "pugliese.sh":
                          line 2:
                                 FIT_GRADE=4

 4 - From the HEADER you MUST know which is the column that you need. In this cases, we used the COLUMNS 7 and 8, that corresponds to the WAVELENGTH AND THE STAR+SKY/UnNormalized.

    4 - a: in "pugliese_corr.py":
                                 lines 31-32          &              37-38: 
                                  wavel1 = data2[7]             wavel2 = data2[7]
                                  spec1 = data2[8]              spec2 = data2[8] 
    
                                 



The program do the complete flux calibration, where first we define in "pugliese_corr.py" the correction by atmospheric extinction.

----------------
----------------

************************    pugliese_corr.py   ************************

1. Find and generate the echelle orders and interpolate the standard and science files to have the same spectral range to work.

2. Get the airmass value from the header,

3. Convert the spectrum in "magnitudes" ->
      Spectrum = -2.5* math.log10(spectrum)

4. Interpolate the extinction values from the table to get the same sampling as for the observed spectrum.

5. Multiply the extinction values by the airmass (ext*airmass)

6. Spectrum = Spectrum - extinction

7. Re-convert the spectrum in flux ->
      Spectrum = 10^(-1*spectrum/2.5) 

----------------
----------------

************************    pugliese_norm.py   ************************

1. Combine the Feige34 spectra (corrected for the extinction, and in flux/sec).

2. Divide the combine spectrum by the theoretical one (attached).

3. Fit the divided spectrum with a polynomial, and save the fit function.

4. Divide your science spectrum (combined of extinction corrected spectra) with the fit.

    

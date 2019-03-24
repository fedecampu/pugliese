REF='./standard/N20180423G0057i.fits'
FIT_GRADE=4

PYTHONWARNINGS="ignore::RuntimeWarning"
LIST=$(ls ./{standard,science}/*.fits)

echo
for i in $LIST; do
    echo " - wavelength calibration and extinction correction for file: '$i'."
    python -W $PYTHONWARNINGS pugliese_corr.py $REF $i
done

echo -n " - normalizing spectrum..."
python -W $PYTHONWARNINGS pugliese_norm.py $FIT_GRADE
echo " done."; echo

return 0

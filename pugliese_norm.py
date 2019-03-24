import sys
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
from sklearn.externals import joblib
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression


def combine_orders(data):

    combined = []
    for o in range(len(data[0])):

        suma = 0.
        for i in range(len(data)):
            suma = data[i][o][1] + suma

        combined.append(suma/(len(data)))

    return combined


def polyfit(x, y, grade=2, plot=False):

    make_poly = PolynomialFeatures(grade)
    x_poly = make_poly.fit_transform(x.reshape(-1, 1))

    model = LinearRegression()
    model.fit(x_poly, y)
    y_fit = model.predict(x_poly)

    return y_fit


#%% Read binary products from 'pipe21.py'.
jobstd = sorted(glob('./standard/*.joblib'))
jobsci = sorted(glob('./science/*.joblib'))

std = []
for j in jobstd:
    std.append(joblib.load(j))

sci = []
for j in jobsci:
    sci.append(joblib.load(j))


#%% Combine spectrums order by order.
combined_std = combine_orders(std)
combined_sci = combine_orders(sci)


#%% Read theoretical spectrum and slice it by orders.
theo_data = np.loadtxt('./standard/ffeige34.dat')
x_theo = theo_data[:,0]/10
y_theo = theo_data[:,1]

theo = []
for o in range(len(combined_std)):
    theo_mask = (x_theo > std[0][o][0][0]) & (x_theo < std[0][o][0][-1])
    theo_interp = np.interp(std[0][o][0], x_theo[theo_mask], y_theo[theo_mask])
    theo.append(theo_interp)


#%% Divide standard combined spectrum by theoretical one.
weighted_std = []
for o in range(len(combined_std)):
    norm = combined_std[o] / theo[o]
    weighted_std.append(norm)


#%% Fit polynomials to weighted spectrum orders.
n = int(sys.argv[1])
fitted = []
for o in range(len(combined_std)):
    n_fit = polyfit(std[0][o][0], weighted_std[o], grade=n)
    fitted.append(n_fit)


#%% Divide combined standard spectrum by fitted.
norm_std = []
for o in range(len(combined_std)):
    norm = combined_std[o] / fitted[o]
    norm_std.append(norm)

for i in range(1, len(norm_std)):
    plt.plot(std[0][i][0], norm_std[i], c='b')
    plt.plot(std[0][i][0], theo[i], c='r')

plt.margins(0.01, 0.05)
plt.title('Normalized standard spectrum with polynomial grade %d fit' % n)
plt.xlabel('Wavelength []')
plt.ylabel('Flux []')
plt.grid(linestyle='--')
plt.savefig('./standard/std_fit.png')


#%% Divide combined science spectrum by fitted.
norm_sci = []
for o in range(len(combined_sci)):
    norm = combined_sci[o] / fitted[o]
    norm_sci.append(norm)


#%% Plot normalized science orders to file.
fig, axs = plt.subplots(figsize=(12, 100), nrows=len(norm_sci), ncols=1)
for i in range(len(norm_sci)):

        axs[i].margins(0.01, 0.05)
        axs[i].set_ylabel('Order %d' % i)
        axs[i].plot(sci[0][i][0], norm_sci[i])

plt.savefig('./science/sci_orders.png', bbox_inches='tight')


#%% Write ASCII output.
full_wavel = std[0][0][0]
for i in range(1, len(std[0])):
    full_wavel = np.concatenate((full_wavel, std[0][i][0]))

full_norm_std = weighted_std[0]
for i in range(1, len(std[0])):
    full_norm_std = np.concatenate((full_norm_std, weighted_std[i]))

full_norm_sci = norm_sci[0]
for i in range(1, len(std[0])):
    full_norm_sci = np.concatenate((full_norm_sci, norm_sci[i]))

np.savetxt('./standard/std_final.txt', np.column_stack((full_wavel, full_norm_std)))
np.savetxt('./science/sci_final.txt', np.column_stack((full_wavel, full_norm_sci)))

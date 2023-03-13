import os
import numpy as np
import matplotlib.pyplot as plt

#import sys, os
#sys.path.append("/home/xisun/petitRADTRANS_official/")
#os.environ['pRT_input_data_path'] = '/net/ipa-gate/export/ipa/quanz/shared/opacity_database/'
#from petitRADTRANS.retrieval.util import getMM

# molecular mass values from https://pubchem.ncbi.nlm.nih.gov/
#MOL_MASS = {
#	'CH4': 16.043, 'CO': 28.010, 'CO2': 44.009, 'H2': 2.016, 'H2O': 18.015, 'K': 39.098, 'Na': 22.99,
#	'N2': 28.014, 'N2O': 44.013, 'NH3': 17.031, 'O2': 31.999, 'O3': 47.998, 'SO2': 64.07
#}
from molmass import Formula




def pt_coefficients(pressures, temperatures, deg=4, print_info=True, make_fig=True, output_dir = None):
	log_pressures = np.log10(pressures)

	coeff = np.polyfit(log_pressures, temperatures, deg=deg)
	print('[Fitted coefficients]')
	for i in range(deg+1):
		print('a_%d: %f' % (deg - i, coeff[i]))
	print()

	if print_info:
		prd_temperature = np.polyval(coeff, log_pressures)
		errors = np.abs(prd_temperature - temperatures)
		rel_errors = errors / temperatures
		print('[Errors]')
		print('Mean error: %f K' % np.mean(errors))
		print('Mean relative error: %f' % np.mean(rel_errors))
		print('Median error: %f K' % np.median(errors))
		print('Median relative error: %f' % np.median(rel_errors))
		max_err_idx = np.argmax(errors)
		print('Max error: %f K at %f bar' % (errors[max_err_idx], pressures[max_err_idx]))
		max_rel_err_idx = np.argmax(errors / temperatures)
		print('Max relative error: %f at %f bar' % (rel_errors[max_rel_err_idx], pressures[max_err_idx]))
		print()

	if make_fig:
		if output_dir is None:
			output_dir = '.'

		fig, ax = plt.subplots(figsize=(6,4))
		ax.set_facecolor('lightgray')
		ax.grid(True, c='white')
		ax.plot(log_pressures, temperatures, label='real')
		ax.plot(log_pressures, prd_temperature, label='polynomial (deg %d)' % deg)
		ax.set_xlabel('Pressure (bar, log scale)')
		ax.set_ylabel('Temperature (K)')
		ax.legend(loc = 'upper left')
		fig.tight_layout()
		fig.savefig(os.path.join(output_dir, 'PT_polynomial_fit.png'))
		plt.close(fig)
	
	return coeff


def nfrac_to_mfrac(nfrac, species, method='surface', layer_weights=None):
	'''
	Converts layered mole mixing ratio to a single set of mass fraction

	[Args]
		nfrac[i,j]: mole fraction of species j in layer i
			NB The layers are arrange from high to low, i.e. the highest layer has i = 0
		species[i]: chemical formula of species i
		method: 'surface' (default) uses the mole fraction on the surface (lowest layer)
			'average' calculates a weighted average using provided weights
			NB If weights are not provided, the simple mean is used
		layer_weights: weights of each layer when using the 'average' method, ignored when using 'surface'
	'''
	assert(nfrac.shape[1] == len(species))

	molecular_weights = np.array([Formula(s).mass for s in species])
	# get mass fractions of each species in each layer
	mfrac = np.empty_like(nfrac)
	for j in range(mfrac.shape[1]):
		mfrac[:,j] = nfrac[:,j] * molecular_weights[j]
	for i in range(nfrac.shape[0]):
		mfrac[i,:] /= np.sum(mfrac[i,:])

	if method == 'surface':
		return mfrac[-1,:]
	elif method == 'average':
		# NB np.average returns the simple mean if weights is None
		return np.average(mfrac, axis=0, weights=layer_weights)
	else:
		raise ValueError('Unknown method to calculate mass fraction.')
	




if __name__ == '__main__':
	pass
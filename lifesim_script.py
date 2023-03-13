import sys
import os
#import petitRADTRANS as spect
#from petitRADTRANS import nat_cst as nc
import numpy as np
import matplotlib.pyplot as plt
#import pandas as pd
import lifesim
from lifesim.util.importer import SpectrumImporter
#from lifesim.util.radiation import black_body
import astropy.units as u
from astropy.constants import R_earth, h, c
from spectres import spectres

#sys.path.append("/home/xisun/petitRADTRANS_official/")
#os.environ['pRT_input_data_path'] = '/net/ipa-gate/export/ipa/quanz/shared/opacity_database/'


# Scale to 10 pc
def scale_flux_to_dist(flux, dist=10, r_planet=1):
    '''
    [Args]
        flux: spectral flux density
        dist: distance of the planet to observer, in parsec
        r_planet: planet radius, in earth radius
    '''
    r_planet = r_planet * R_earth
    dist = (10 * u.parsec).to(u.meter)
    scaled_flux = (R_earth**2 / dist**2) * flux
    return scaled_flux


def get_lifesim_snr(
    input_file,
    do_bb=True, # if set to True, blackbody spectrum, if set to false, Sarah Rugheimers Earth spectra
    opt_wl=15, # wavelength for which the transmission is optimized in micron
    planet_temp=285, # planet effective temperature in K
    planet_radius=1, # planet effective radius in Earth_radii
    planet_angsep=0.1, # planet angular separation from host star in arcsec
    sys_distance=10, # distance to the target system in pc
    star_temp=5778, # star effective temperature in K
    star_radius=1, # star effective radius in Solar_radii
    integration_time=1*60*60, # overall integration time in s
    n_phi=360, # number of sub-integrations / rotation steps
    zodi=3, # exozodi level in zodis
    spec_res=50 # resolving power
):
    # create bus
    bus = lifesim.Bus()

    # setting the options
    bus.data.options.set_scenario('baseline')

    # ---------- Creating the Instrument ----------

    bus.data.options.set_manual(wl_optimal=opt_wl)
    bus.data.options.set_manual(spec_res=spec_res)

    # create modules and add to bus
    instrument = lifesim.Instrument(name='inst')
    bus.add_module(instrument)

    transm = lifesim.TransmissionMap(name='transm')
    bus.add_module(transm)

    exo = lifesim.PhotonNoiseExozodi(name='exo')
    bus.add_module(exo)
    local = lifesim.PhotonNoiseLocalzodi(name='local')
    bus.add_module(local)
    star = lifesim.PhotonNoiseStar(name='star')
    bus.add_module(star)

    # connect all modules
    bus.connect(('inst', 'transm'))
    bus.connect(('inst', 'exo'))
    bus.connect(('inst', 'local'))
    bus.connect(('inst', 'star'))

    bus.connect(('star', 'transm'))


    # ---------- Importing the earth spectrum ----------

    importer = SpectrumImporter()
    importer.do_import(pathtotext=input_file,
                    x_string='micron',
                    y_string='ph m-2 s-1 micron-1',
                    radius_p_spectrum=None,
                    radius_p_target=planet_radius,
                    distance_s_spectrum=None,
                    distance_s_target=sys_distance,
                    integration_time=0)

    flux_planet_spectrum = [importer.x_data, importer.y_data]

    # run the simulation to get the noise rates

    snr1h, flux, noise = instrument.get_spectrum(temp_s=star_temp,  # in K
                                            radius_s=star_radius,  # in R_sun
                                            distance_s=sys_distance,  # in pc
                                            lat_s=0.78,  # in radians
                                            z=zodi,  # in zodis
                                            angsep=planet_angsep,  # in arcsec
                                            flux_planet_spectrum=flux_planet_spectrum,  # in ph m-3 s-1 over m
                                            integration_time=integration_time,  # in s
                                            safe_mode=True)
    
    return snr1h[0]*u.meter, snr1h[1]


def resample_to_wlen(wlen, flux, wlen_new):
    # add an additional data point so that spectres doesn't complain about "out of range"
    # TODO: find solution that deals with any wavelength range, e.g. extrapolation
    wlen = np.concatenate(([3.9997e-6], wlen))
    flux = np.concatenate(([flux[0]], flux))
    # rebin to new resolution
    flux_new = spectres(wlen_new, wlen, flux)
    return flux_new


def scale_snr_to_ref(wlen, snr, ref_snr=10, ref_wlen=11.25):
    closest_wlen_idx = np.argmin(np.abs(wlen - ref_wlen))
    scaled_snr = snr * (ref_snr / snr[closest_wlen_idx])
    return scaled_snr 


def generate_prt_input(input_spec, output_dir):
    '''
    Steps:
    1. scale the spectrum assuming the planet is 10 pc away (done)
    2. convert to photon/m2/s/micron (done)
    3. set up LIFESim script options if necessary (done)
    4. after LIFESim section, scale output SNR so that it is e.g. 10 at 11.25 micron (done)
    5. scale back to petitRADTRANS-friendly units, erg m^2 s-1 Hz-1 (done)
    '''
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    input_lifesim = os.path.join(output_dir, 'input_lifesim.txt')
    input_prt = os.path.join(output_dir, 'input_prt.txt')

    # Read raw data
    data = np.loadtxt(input_spec, dtype=float, skiprows=2)[::-1,:] # LIFEsim requires increasing order of wavelengths
    wlen = data[:,0] * u.micron
    flux = data[:,1] * u.joule / u.second / u.meter**2 / u.micron

    # scale to 10 pc
    flux = scale_flux_to_dist(flux)
    
    # Convert to photon / m^2 / s / micron
    flux = flux / (h * c / wlen.to(u.meter)) * u.photon

    np.savetxt(
        input_lifesim,
        np.stack((wlen.value, flux.value), axis = 1),
        fmt=['%.4f', '%.7e']
    ) # save intermediate result
    
    wlen_new, snr = get_lifesim_snr(input_lifesim)
    wlen_new = wlen_new.to(u.micron) # wavelength returned by LIFEsim is in metres

    flux_new = resample_to_wlen(wlen.value, flux.value, wlen_new.value)
    flux_new *= u.photon / u.meter**2 / u.second / u.micron

    snr_scaled = scale_snr_to_ref(wlen_new.value, snr)

    # Convert flux to erg * m^2 / s / Hz
    flux_new *= wlen_new * h.to(u.joule / u.hertz) / u.photon # first convert to J / m^2 / s / Hz
    flux_new = flux_new.to(u.erg / u.meter**2 / u.second / u.hertz) # then convert J to erg

    np.savetxt(
        input_prt,
        np.stack((wlen_new.value, flux_new.value, flux_new.value / snr_scaled), axis = 1),
        fmt=['%.16f', '%.16e', '%.16e']
    ) # save final result
    
    
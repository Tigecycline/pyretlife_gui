#import pandas as pd
import yaml
import os

from constants import PRIOR_PARAM_NAMES




class ConfigHandler:
    SECTIONS = [
        'GROUND TRUTH DATA',
        'RUN SETTINGS',
        'TEMPERATURE PARAMETERS',
        'PHYSICAL PARAMETERS',
        'CHEMICAL COMPOSITION PARAMETERS',
        'SCATTERING PARAMETERS',
        'CLOUD PARAMETERS',
        'USER-DEFINED UNITS'
    ]


    def __init__(self, config=None):
        if config is None:
            self.use_default_config()
        elif isinstance(config, dict):
            self.config = config
        elif isinstance(config, str):
            self.read_yaml(config)
        else:
            raise TypeError('[ConfigHandler.__init__] config must either a dictionary or a path.')
            
        self.verify_sections()
    

    def __getitem__(self, key):
        return self.config[key]
    

    def __setitem__(self, key, value):
        self.config[key] = value


    def verify_sections(self):
        for section in ConfigHandler.SECTIONS:
            if section not in self.config.keys():
                raise KeyError('[ConfigHandler.verify_sections] Section %s not found in config.' % section)


    def read_yaml(self, yaml_path):
        with open(yaml_path, 'r') as yaml_file:
            self.config = yaml.safe_load(yaml_file)
    

    def write_yaml(self, yaml_path=None):
        if yaml_path is None:
            yaml_path = os.path.join('./config.yaml')
        elif os.path.isdir(yaml_path):
            yaml_path = os.path.join(yaml_path, 'config.yaml')
        #print(yaml_path)
        
        with open(yaml_path, 'w') as yaml_file:
            yaml.dump(self.config, yaml_file, sort_keys=False)

    
    def use_default_config(self):
        # TODO?: store the default somewhere else, e.g. in a file
        self.config = {section: {} for section in ConfigHandler.SECTIONS}

        self['GROUND TRUTH DATA']['input_profile'] = '/net/ipa-gate/export/ipa/quanz/user_accounts/konradb/Retrieval_Inputs/Timmy/PT_Timmy_2.txt'
        self['GROUND TRUTH DATA']['data_files'] = ['/net/ipa-gate/export/ipa/quanz/user_accounts/konradb/Retrieval_Inputs/Timmy/Earth_Timmy_R200_ph_SN_10_2.txt']

        self['RUN SETTINGS']['wavelength_range'] = [3, 20]
        self['RUN SETTINGS']['output_folder'] = '.'
        self['RUN SETTINGS']['live_points'] = 600
        self['RUN SETTINGS']['include_scattering'] = {'Rayleigh': True, 'thermal': True, 'direct_light': True, 'clouds': False}
        self['RUN SETTINGS']['include_CIA'] = True
        self['RUN SETTINGS']['include_moon'] = False
        self['RUN SETTINGS']['parameterization'] = 'polynomial'
        self['RUN SETTINGS']['vae_net'] = 'decoder.onx'
        self['RUN SETTINGS']['top_log_pressure'] = -6.
        self['RUN SETTINGS']['n_layers'] = 100

        for param in ['a_4', 'a_3', 'a_2', 'a_1', 'a_0']:
            self['TEMPERATURE PARAMETERS'][param] = {}
        self['TEMPERATURE PARAMETERS']['a_4'] = param_dict('uniform', [2., 5.], 3.67756393)
        self['TEMPERATURE PARAMETERS']['a_3'] = param_dict('uniform', [0., 100.], 136.42147966)
        self['TEMPERATURE PARAMETERS']['a_2'] = param_dict('uniform', [0., 300.], 182.6557084)
        self['TEMPERATURE PARAMETERS']['a_1'] = param_dict('uniform', [0., 100.], 136.42147966)
        self['TEMPERATURE PARAMETERS']['a_0'] = param_dict('uniform', [0., 600.], 292.92802205)

        for param in ['P0', 'd_syst', 'R_pl', 'M_pl']:
            self['PHYSICAL PARAMETERS'][param] = {}
        self['PHYSICAL PARAMETERS']['P0'] = param_dict('log-uniform', [-2, 2], 1.0294)
        self['PHYSICAL PARAMETERS']['d_syst'] = param_dict(truth=10.)
        self['PHYSICAL PARAMETERS']['R_pl'] = param_dict('gaussian', [1, 0.2], 1., unit='Rearth')
        self['PHYSICAL PARAMETERS']['M_pl'] = param_dict('log-gaussian', [0, 0.4], 1.)

        self['CHEMICAL COMPOSITION PARAMETERS']['settings'] = {'resolution': 200, 'mmw_inert': 28.}
        for species in ['N2', 'O2', 'CO2', 'CH4', 'H2O', 'O3', 'CO', 'N2O']:
            self['CHEMICAL COMPOSITION PARAMETERS'][species] = {}
        self['CHEMICAL COMPOSITION PARAMETERS']['N2'] = param_dict('log-uniform', [-2, 0], 0.78)
        self['CHEMICAL COMPOSITION PARAMETERS']['O2'] = param_dict('log-uniform', [-2, 0], 0.20, ['O2_main_HN16_HH_Chubb', 'O2_UV'])
        self['CHEMICAL COMPOSITION PARAMETERS']['CO2'] = param_dict('log-uniform', [-15, 0], 0.004, ['CO2_main_HN20_air_C25', 'CO2_UV'])
        self['CHEMICAL COMPOSITION PARAMETERS']['CH4'] = param_dict('log-uniform', [-15, 0], 0.0000017, ['CH4_main_HN20_air_C25', 'CH4_UV'])
        self['CHEMICAL COMPOSITION PARAMETERS']['H2O'] = param_dict('log-uniform', [-15, 0], 0.001, ['H2O_main_HN20_air_C25', 'H2O_UV'])
        self['CHEMICAL COMPOSITION PARAMETERS']['O3'] = param_dict('log-uniform', [-15, 0], 0.0000003, ['O3_main_HN20_air_C25', 'O3_UV'])
        self['CHEMICAL COMPOSITION PARAMETERS']['CO'] = param_dict('log-uniform', [-15, 0], 0.000000125, ['CO_main_HN20_air_C25', 'CO_UV'])
        self['CHEMICAL COMPOSITION PARAMETERS']['N2O'] = param_dict('log-uniform', [-15, 0], 0.00000032, ['N2O_main_HN20_air_C25', 'N2O_UV'])

        self['SCATTERING PARAMETERS']['reflectance'] = param_dict(truth=0.1)
        self['SCATTERING PARAMETERS']['emissivity'] = param_dict(truth=1.)
        self['SCATTERING PARAMETERS']['stellar_temperature'] = param_dict(truth=5778.)
        self['SCATTERING PARAMETERS']['stellar_radius'] = param_dict(truth=1.)
        self['SCATTERING PARAMETERS']['semimajor_axis'] = param_dict(truth=1.)

        self['CLOUD PARAMETERS']['composition'] = 'transparent'

        self['USER-DEFINED UNITS']['R_sun'] = '1m'




def param_dict(kind='(known)', params=None, truth=None, lines=None, unit=None):
    result = {}

    if lines is not None:
        result['lines'] = lines

    if kind == '(known)':
        if truth is None:
            raise TypeError('[prior_dict] For known parameters, a truth value must be provided.')
    else:
        result['prior'] = {}

        if not isinstance(params, list):
            raise TypeError('[prior_dict] Prior parameters must be provided in a list.')
        result['prior']['kind'] = kind

        try:
            param_names = PRIOR_PARAM_NAMES[kind]
        except KeyError:
            raise ValueError('[prior_dict] Unknown prior type.')
        result['prior']['prior_specs'] = {name: value for name, value in zip(param_names, params)}

    if truth is not None:
        result['truth'] = truth
    
    if unit is not None:
        result['unit'] = unit

    return result




if __name__ == '__main__':
    handler = ConfigHandler()
    handler.write_yaml()
    ref_handler = ConfigHandler('./reference.yaml')

    for key in handler.config.keys():
        if handler[key] != ref_handler[key]:
            print(key)
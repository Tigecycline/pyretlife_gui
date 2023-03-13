SPECIES_NAMES = {
    'CH4': 'methane',
    'CO': 'carbon monoxide',
    'CO2': 'carbon dioxide',
    'H2': 'hydrogen',
    'H2O': 'water',
    'H2S': 'hydrogen sulfide',
    'K': 'potassium',
    'N2': 'nitrogen',
    'N2O': 'nitrous oxide',
    'Na': 'sodium',
    'NH3': 'ammonia',
    'O2': 'oxygen',
    'O3': 'ozone',
    'OCS': 'carbonyl sulfide',
    'OH': 'hydroxide',
    'PH3': 'phosphine',
    'SiO': 'silicon monoxide',
    'SO2': 'sulfur dioxide'
}

PRIOR_PARAM_NAMES = {
    '(known)': [],
    'uniform': ['lower', 'upper'],
    'log-uniform': ['log_lower', 'log_upper'],
    'gaussian': ['mean', 'sigma'],
    'log-gaussian': ['log_mean', 'log_sigma']
}
# TODO?: use a yaml file instead

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

PT_PARAMETERIZATIONS = {
    'polynomial 4': ['a_%d' % i for i in range(5)]
}

LINE_SPECS = {
    # NB Resolution must the last one and a default resolution has to be specified
    # For all other specs, the default is not required
    'Isotope': {'options': ['all', 'main'], 'default': 'main'},
    'Database': {'options': ['EX21', 'HP10', 'HN20', 'PK95'], 'default': 'HN20'},
    'Broadening': {'options': ['air', 'CO2', 'HH', 'H2O'], 'default': 'air'},
    'Cutoff': {'options': ['C25', 'C100', 'Chubb', 'BG69', 'HB02', 'nocut'], 'default': 'C25'},
    'Resolution': {'options': ['50', '100', '200', '1000'], 'default': '50'}
}
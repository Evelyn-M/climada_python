"""
Fill Measures from MATLAB file.
"""

__all__ = ['DEF_VAR_MAT',
           'DEF_VAR_EXCEL',
           'read'
          ]

import os
import logging
import numpy as np
import pandas

from climada.entity.measures.measure import Measure
import climada.util.hdf5_handler as hdf5
from climada.entity.tag import Tag

DEF_VAR_MAT = {'sup_field_name': 'entity',      
               'field_name': 'measures',
               'var_name': {'name' : 'name',
                            'color' : 'color',
                            'cost' : 'cost',
                            'haz_int_a' : 'hazard_intensity_impact_a',
                            'haz_int_b' : 'hazard_intensity_impact_b',
                            'haz_frq' : 'hazard_high_frequency_cutoff',
                            'haz_set' : 'hazard_event_set',
                            'mdd_a' : 'MDD_impact_a',
                            'mdd_b' : 'MDD_impact_b',
                            'paa_a' : 'PAA_impact_a',
                            'paa_b' : 'PAA_impact_b',
                            'risk_att' : 'risk_transfer_attachement',
                            'risk_cov' : 'risk_transfer_cover'
                           }
              }

DEF_VAR_EXCEL = {'sheet_name': 'measures',
                 'col_name': {'name' : 'name',
                              'color' : 'color',
                              'cost' : 'cost',
                              'haz_int' : 'hazard intensity impact',
                              'haz_frq' : 'hazard high frequency cutoff',
                              'haz_set' : 'hazard event set',
                              'mdd_a' : 'MDD impact a',
                              'mdd_b' : 'MDD impact b',
                              'paa_a' : 'PAA impact a',
                              'paa_b' : 'PAA impact b',
                              'risk_att' : 'risk transfer attachement',
                              'risk_cov' : 'risk transfer cover'
                             }
                }

LOGGER = logging.getLogger(__name__)

def read(meas, file_name, description, var_names):
    """Read file and store variables in MeasureSet. """
    meas.tag = Tag(file_name, description)
    
    extension = os.path.splitext(file_name)[1]
    if extension == '.mat':
        try:
            read_mat(meas, file_name, var_names)
        except KeyError as var_err:
            LOGGER.error("Not existing variable. " + str(var_err))
            raise var_err
    elif (extension == '.xlsx') or (extension == '.xls'):
        try:
            read_excel(meas, file_name, var_names)
        except KeyError as var_err:
            LOGGER.error("Not existing variable. " + str(var_err))
            raise var_err    
    else:
        LOGGER.error('Input file extension not supported: %s.', extension)
        raise ValueError

def read_mat(measures, file_name, var_names):
    """Read MATLAB file and store variables in measures."""
    if var_names is None:
        var_names = DEF_VAR_MAT
        
    data = hdf5.read(file_name)
    try:
        data = data[var_names['sup_field_name']]
    except KeyError:
        pass
    data = data[var_names['field_name']]

    num_mes = len(data[var_names['var_name']['name']])
    for idx in range(0, num_mes):
        meas = Measure()

        meas.name = hdf5.get_str_from_ref(
            file_name, data[var_names['var_name']['name']][idx][0])

        color_str = hdf5.get_str_from_ref(
            file_name, data[var_names['var_name']['color']][idx][0])
        meas.color_rgb = np.fromstring(color_str, dtype=float, sep=' ')
        meas.cost = data[var_names['var_name']['cost']][idx][0]
        meas.hazard_freq_cutoff = \
                                data[var_names['var_name']['haz_frq']][idx][0]
        meas.hazard_event_set = hdf5.get_str_from_ref(
            file_name, data[var_names['var_name']['haz_set']][idx][0])
        meas.hazard_intensity = ( \
                data[var_names['var_name']['haz_int_a']][idx][0], \
                data[var_names['var_name']['haz_int_b']][0][idx])
        meas.mdd_impact = (data[var_names['var_name']['mdd_a']][idx][0],
                           data[var_names['var_name']['mdd_b']][idx][0])
        meas.paa_impact = (data[var_names['var_name']['paa_a']][idx][0],
                           data[var_names['var_name']['paa_b']][idx][0])
        meas.risk_transf_attach = \
                                data[var_names['var_name']['risk_att']][idx][0]
        meas.risk_transf_cover = \
                                data[var_names['var_name']['risk_cov']][idx][0]

        measures.add_measure(meas)

def read_excel(measures, file_name, var_names):
    """Read excel file and store variables in measures."""
    if var_names is None:
        var_names = DEF_VAR_EXCEL

    dfr = pandas.read_excel(file_name, var_names['sheet_name'])

    num_mes = len(dfr.index)
    for idx in range(0, num_mes):
        meas = Measure()

        meas.name = dfr[var_names['col_name']['name']][idx]
        meas.color_rgb = np.fromstring( \
            dfr[var_names['col_name']['color']][idx], dtype=float, sep=' ')
        meas.cost = dfr[var_names['col_name']['cost']][idx]
        meas.hazard_freq_cutoff = dfr[var_names['col_name']['haz_frq']][idx]
        meas.hazard_event_set = dfr[var_names['col_name']['haz_set']][idx]
        # Search for (a, b) values, put a = 1 otherwise
        try:
            meas.hazard_intensity = (1, dfr[var_names['col_name']['haz_int']]\
                                    [idx])
        except KeyError:
            col_name_a = var_names['col_name']['haz_int'] + ' a'
            col_name_b = var_names['col_name']['haz_int'] + ' b'
            meas.hazard_intensity = (dfr[col_name_a][idx], \
                                     dfr[col_name_b][idx])
        meas.mdd_impact = (dfr[var_names['col_name']['mdd_a']][idx],
                           dfr[var_names['col_name']['mdd_b']][idx])
        meas.paa_impact = (dfr[var_names['col_name']['paa_a']][idx],
                           dfr[var_names['col_name']['paa_b']][idx])
        meas.risk_transf_attach = dfr[var_names['col_name']['risk_att']][idx]
        meas.risk_transf_cover = dfr[var_names['col_name']['risk_cov']][idx]

        measures.add_measure(meas)
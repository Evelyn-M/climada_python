"""
Test MeasuresMat class.
"""

import unittest
import numpy as np

from climada.entity.measures.base import Measures
from climada.entity.measures import source_mat as mat
from climada.util.constants import ENT_DEMO_MAT
 
class TestReader(unittest.TestCase):
    """Test reader functionality of the MeasuresMat class"""

    def tearDown(self):
        mat.VAR_NAMES = {'name' : 'name',
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

    def test_demo_file(self):
        # Read demo excel file
        meas = Measures()
        description = 'One single file.'
        meas.read(ENT_DEMO_MAT, description)

        # Check results        
        n_meas = 4
        
        self.assertEqual(len(meas.get_action()), n_meas)
        
        act_man = meas.get_action('Mangroves')
        self.assertEqual(act_man.name, 'Mangroves')
        self.assertEqual(type(act_man.color_rgb), np.ndarray)
        self.assertEqual(len(act_man.color_rgb), 3)
        self.assertEqual(act_man.color_rgb[0], 0.1529)
        self.assertEqual(act_man.color_rgb[1], 0.251)
        self.assertEqual(act_man.color_rgb[2], 0.5451)
        self.assertEqual(act_man.cost, 1311768360.8515418)
        self.assertEqual(act_man.hazard_freq_cutoff, 0)
#        self.assertEqual(meas._data[first].hazard_event_set, 'nil')
        self.assertEqual(act_man.hazard_intensity, (1, -4))
        self.assertEqual(act_man.mdd_impact, (1, 0))
        self.assertEqual(act_man.paa_impact, (1, 0))
        self.assertEqual(act_man.risk_transf_attach, 0)
        self.assertEqual(act_man.risk_transf_cover, 0)

        act_buil = meas.get_action('Building code')
        self.assertEqual(act_buil.name, 'Building code')
        self.assertEqual(type(act_buil.color_rgb), np.ndarray)
        self.assertEqual(len(act_buil.color_rgb), 3)
        self.assertEqual(act_buil.color_rgb[0], 0.6980)
        self.assertEqual(act_buil.color_rgb[1], 0.8745)
        self.assertEqual(act_buil.color_rgb[2], 0.9333)
        self.assertEqual(act_buil.cost, 9200000000.0000000)
        self.assertEqual(act_buil.hazard_freq_cutoff, 0)
#        self.assertEqual(meas._data[n_meas-1].hazard_event_set, 'nil')
        self.assertEqual(act_buil.hazard_intensity, (1, 0))
        self.assertEqual(act_buil.mdd_impact, (0.75, 0))
        self.assertEqual(act_buil.paa_impact, (1, 0))
        self.assertEqual(act_buil.risk_transf_attach, 0)
        self.assertEqual(act_buil.risk_transf_cover, 0)

        self.assertEqual(meas.tag.file_name, ENT_DEMO_MAT)
        self.assertEqual(meas.tag.description, description)

    def test_wrong_file_fail(self):
        """ Read file intensity, fail."""
        meas = Measures()
        mat.VAR_NAMES['mdd_a'] = 'wrong name'
        with self.assertRaises(KeyError):
            meas.read(ENT_DEMO_MAT)

# Execute Tests
TESTS = unittest.TestLoader().loadTestsFromTestCase(TestReader)
unittest.TextTestRunner(verbosity=2).run(TESTS)
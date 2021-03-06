import os
import sys
import unittest
import matplotlib

from climada.util.constants import SOURCE_DIR

def find_unit_tests():
    """ select unit tests."""
    suite = unittest.TestLoader().discover('climada.entity.exposures.test')
    suite.addTest(unittest.TestLoader().discover('climada.entity.disc_rates.test'))
    suite.addTest(unittest.TestLoader().discover('climada.entity.impact_funcs.test'))
    suite.addTest(unittest.TestLoader().discover('climada.entity.measures.test'))
    suite.addTest(unittest.TestLoader().discover('climada.entity.test'))
    suite.addTest(unittest.TestLoader().discover('climada.hazard.test'))
    suite.addTest(unittest.TestLoader().discover('climada.hazard.centroids.test'))
    suite.addTest(unittest.TestLoader().discover('climada.engine.test'))
    suite.addTest(unittest.TestLoader().discover('climada.util.test'))
    return suite

def find_integ_tests():
    """ select integration tests."""
    suite = unittest.TestLoader().discover('climada.test')
    return suite

def main():
    """ parse input argument: None, 'unit' or 'integ'. Execute accordingly."""
    if sys.argv[1:]:
        import xmlrunner
        arg = sys.argv[1]
        if arg == 'unit':
            output = os.path.join(SOURCE_DIR, '../tests_xml')
            xmlrunner.XMLTestRunner(output=output).run(find_unit_tests())
        elif arg == 'integ':
            output = os.path.join(SOURCE_DIR, '../tests_xml')
            xmlrunner.XMLTestRunner(output=output).run(find_integ_tests())
    else:
        # execute without xml reports
        unittest.TextTestRunner(verbosity=2).run(find_unit_tests())

if __name__ == '__main__':
    matplotlib.use("Agg")
    sys.path.append(os.getcwd())
    main()

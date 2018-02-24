"""
Test Centroids base class.
"""

import unittest
import warnings
from array import array
import numpy as np

from climada.hazard.centroids.base import Centroids
from climada.entity.tag import Tag

class TestLoader(unittest.TestCase):
    """Test loading funcions from the Centroids class"""

    @staticmethod
    def good_centroids():
        """Define well a Centroids"""
        cen = Centroids()
        cen.coord = np.array([[1, 2], [3, 4], [5, 6]])
        cen.id = np.array([1, 2, 3])
        cen.region_id = np.array([1, 2, 3])

        return cen

    def test_check_wrongCoord_fail(self):
        """Wrong centroids definition"""
        cen = self.good_centroids()
        cen.coord = np.array([[1, 2],[3, 4]])

        with self.assertRaises(ValueError) as error:
            cen.check()
        self.assertEqual('Invalid Centroids.coord row size: 3 != 2', \
                         str(error.exception))

    def test_check_wrongRegion_fail(self):
        """Wrong centroids definition"""
        cen = self.good_centroids()
        cen.region_id = np.array([1, 2])

        with self.assertRaises(ValueError) as error:
            cen.check()
        self.assertEqual('Invalid Centroids.region_id size: 3 != 2', \
                         str(error.exception))

    def test_check_wrongId_fail(self):
        """Wrong centroids definition"""
        cen = self.good_centroids()
        cen.id = np.array([1, 2, 2])

        with self.assertRaises(ValueError) as error:
            cen.check()
        self.assertEqual('There are centroids with the same identifier.', \
                         str(error.exception))

class TestAppend(unittest.TestCase):
    """Test append function."""
   
    def test_appended_type(self):
        """Append the same centroids."""
        centr1 = Centroids()
        centr1.tag = Tag('file_1.mat', 'description 1')
        centr1.coord = np.array([[1, 2], [3, 4], [5, 6]])
        centr1.id = np.array([5, 7, 9])
        centr2 = centr1
        new_pos = centr1.append(centr2)
        self.assertEqual(type(centr1.tag.file_name), str)
        self.assertEqual(type(centr1.tag.description), str)
        self.assertEqual(type(centr1.coord), np.ndarray)
        self.assertEqual(type(centr1.id), np.ndarray)
        self.assertTrue(type(new_pos), array)
        self.assertTrue(type(centr1.region_id), np.ndarray)

    def test_append_empty_fill(self):
        """Append the same centroids."""
        centr1 = Centroids()
        centr1.tag = Tag('file_1.mat', 'description 1')
        centr1.coord = np.array([[1, 2], [3, 4], [5, 6]])
        centr1.id = np.array([5, 7, 9])
        centr2 = Centroids()
        new_pos = centr1.append(centr2)
        self.assertEqual(centr1.tag.file_name, 'file_1.mat')
        self.assertEqual(centr1.tag.description, 'description 1')
        self.assertEqual(centr1.coord.shape, (3, 2))
        self.assertTrue(np.array_equal(centr1.coord[0, :], [1, 2]))
        self.assertTrue(np.array_equal(centr1.coord[1, :], [3, 4]))
        self.assertTrue(np.array_equal(centr1.coord[2, :], [5, 6]))
        self.assertEqual(centr1.id.shape, (3,))
        self.assertTrue(np.array_equal(centr1.id, np.array([5, 7, 9])))
        self.assertTrue(np.array_equal(new_pos, []))
        self.assertTrue(np.array_equal(centr1.region_id, np.array([], \
                         np.int64)))

    def test_append_to_empty_fill(self):
        """Append to empty centroids."""
        centr1 = Centroids()
        centr2 = Centroids()
        centr2.tag = Tag('file_1.mat', 'description 1')
        centr2.coord = np.array([[1, 2], [3, 4], [5, 6]])
        centr2.id = np.array([5, 7, 9])
        new_pos = centr1.append(centr2)
        self.assertEqual(centr1.tag.file_name, 'file_1.mat')
        self.assertEqual(centr1.tag.description, 'description 1')
        self.assertEqual(centr1.coord.shape, (3, 2))
        self.assertTrue(np.array_equal(centr1.coord[0, :], [1, 2]))
        self.assertTrue(np.array_equal(centr1.coord[1, :], [3, 4]))
        self.assertTrue(np.array_equal(centr1.coord[2, :], [5, 6]))
        self.assertEqual(centr1.id.shape, (3,))
        self.assertTrue(np.array_equal(centr1.id, np.array([5, 7, 9])))
        self.assertTrue(np.array_equal(new_pos, [0, 1, 2]))
        self.assertTrue(np.array_equal(centr1.region_id, np.array([], \
                         np.int64)))

    def test_same_centroids_pass(self):
        """Append the same centroids."""
        centr1 = Centroids()
        centr1.tag = Tag('file_1.mat', 'description 1')
        centr1.coord = np.array([[1, 2], [3, 4], [5, 6]])
        centr1.id = np.array([5, 7, 9])
        
        centr2 = centr1
        
        new_pos = centr1.append(centr2)
        self.assertEqual(centr1.tag.file_name, 'file_1.mat')
        self.assertEqual(centr1.tag.description, 'description 1')
        self.assertEqual(centr1.coord.shape, (3, 2))
        self.assertTrue(np.array_equal(centr1.coord[0, :], [1, 2]))
        self.assertTrue(np.array_equal(centr1.coord[1, :], [3, 4]))
        self.assertTrue(np.array_equal(centr1.coord[2, :], [5, 6]))
        self.assertEqual(centr1.id.shape, (3,))
        self.assertTrue(np.array_equal(centr1.id, np.array([5, 7, 9])))
        self.assertTrue(np.array_equal(new_pos, [0, 1, 2]))
        self.assertTrue(np.array_equal(centr1.region_id, np.array([], \
                         np.int64)))

    def test_new_elem_pass(self):
        """Append a centroids with a new element."""
        centr1 = Centroids()
        centr1.tag = Tag('file_1.mat', 'description 1')
        centr1.coord = np.array([[1, 2], [3, 4], [5, 6]])
        centr1.id = np.array([5, 7, 9])
        centr1.region_id = np.array([1, 2, 3])
        
        centr2 = Centroids()
        centr2.tag = Tag('file_2.mat', 'description 2')
        centr2.coord = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        centr2.id = np.array([6, 7, 9, 1])
        centr2.region_id = np.array([3, 4, 5, 6])
        
        new_pos = centr1.append(centr2)
        self.assertEqual(len(centr1.tag.file_name), 2)
        self.assertEqual(len(centr1.tag.description), 2)
        self.assertEqual(centr1.coord.shape, (4, 2))
        self.assertTrue(np.array_equal(centr1.coord[0, :], [1, 2]))
        self.assertTrue(np.array_equal(centr1.coord[1, :], [3, 4]))
        self.assertTrue(np.array_equal(centr1.coord[2, :], [5, 6]))
        self.assertTrue(np.array_equal(centr1.coord[3, :], [7, 8]))
        self.assertEqual(centr1.id.shape, (4,))
        self.assertTrue(\
                         np.array_equal(centr1.id, np.array([6, 7, 9, 1])))
        self.assertTrue(\
                         np.array_equal(centr1.region_id, np.array([3, 4, 5, 6])))
        self.assertTrue(np.array_equal(new_pos, [0, 1, 2, 3]))

    def test_all_new_elem_pass(self):
        """Append a centroids with a new element."""
        centr1 = Centroids()
        centr1.tag = Tag('file_1.mat', 'description 1')
        centr1.coord = np.array([[1, 2], [3, 4], [5, 6]])
        centr1.id = np.array([5, 7, 9])
        
        centr2 = Centroids()
        centr2.tag = Tag('file_2.mat', 'description 2')
        centr2.coord = np.array([[7, 8], [1, 5]])
        centr2.id = np.array([5, 7])
        
        new_pos = centr1.append(centr2)
        self.assertEqual(len(centr1.tag.file_name), 2)
        self.assertEqual(len(centr1.tag.description), 2)
        self.assertEqual(centr1.coord.shape, (5, 2))
        self.assertTrue(np.array_equal(centr1.coord[0, :], [1, 2]))
        self.assertTrue(np.array_equal(centr1.coord[1, :], [3, 4]))
        self.assertTrue(np.array_equal(centr1.coord[2, :], [5, 6]))
        self.assertTrue(np.array_equal(centr1.coord[3, :], [7, 8]))
        self.assertTrue(np.array_equal(centr1.coord[4, :], [1, 5]))
        self.assertEqual(centr1.id.shape, (5,))
        self.assertTrue(np.array_equal(centr1.id, \
                                              np.array([5, 7, 9, 10, 11])))
        self.assertTrue(np.array_equal(centr1.region_id, np.array([], \
                         np.int64)))
        self.assertTrue(np.array_equal(new_pos, [3, 4]))

    def test_without_region_pass(self):
        """Append centroids without region id."""
        centr1 = Centroids()
        centr1.tag = Tag('file_1.mat', 'description 1')
        centr1.coord = np.array([[1, 2], [3, 4], [5, 6]])
        centr1.id = np.array([5, 7, 9])
        
        centr2 = Centroids()
        centr2.tag = Tag('file_2.mat', 'description 2')
        centr2.coord = np.array([[1, 2], [3, 4], [5, 6]])
        centr2.id = np.array([5, 7, 9])
        centr2.region_id = np.array([1, 1, 1])
        
        with warnings.catch_warnings(record=True) as w:
            centr1.append(centr2)
        self.assertTrue(np.array_equal(centr1.region_id, np.array([], \
                         np.int64)))
        self.assertIn("Centroids.region_id is not going to be set.", \
                      str(w[1].message))

        centr1 = Centroids()
        centr1.tag = Tag('file_1.mat', 'description 1')
        centr1.coord = np.array([[1, 2], [3, 4], [5, 6]])
        centr1.id = np.array([5, 7, 9])
        centr1.region_id = np.array([1, 1, 1])
        
        centr2 = Centroids()
        centr2.tag = Tag('file_2.mat', 'description 2')
        centr2.coord = np.array([[1, 2], [3, 4], [5, 6]])
        centr2.id = np.array([5, 7, 9])
        
        with warnings.catch_warnings(record=True) as w:
            centr1.append(centr2)
        self.assertTrue(np.array_equal(centr1.region_id, np.array([], \
                         np.int64)))
        self.assertIn("Centroids.region_id is not going to be set.", \
                      str(w[1].message))

    def test_with_region_pass(self):
        """Append the same centroids with region id."""
        centr1 = Centroids()
        centr1.tag = Tag('file_1.mat', 'description 1')
        centr1.coord = np.array([[1, 2], [3, 4], [5, 6]])
        centr1.id = np.array([5, 7, 9])
        centr1.region_id = np.array([1, 1, 1])
        
        centr2 = centr1
        
        centr1.append(centr2)
        self.assertTrue(np.array_equal(centr1.region_id, \
                                              np.array([1, 1, 1])))

# Execute Tests
TESTS = unittest.TestLoader().loadTestsFromTestCase(TestLoader)
TESTS.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAppend))
unittest.TextTestRunner(verbosity=2).run(TESTS)
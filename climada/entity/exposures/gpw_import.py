# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 10:11:45 2018

@author: Dario
"""
import os
import logging
import subprocess

import gdal
import pandas as pd
from scipy import ndimage as nd
import numpy as np

from climada.util.constants import SYSTEM_DIR
from climada.entity.exposures import litpop as LitPop
logging.root.setLevel(logging.DEBUG)
LOGGER = logging.getLogger(__name__)

FILENAME_GPW = 'gpw_v4_population_count_rev10_2015_30_sec.tif'
BUFFER_VAL = -340282306073709652508363335590014353408
# Hard coded value which is used for NANs in original GPW data

def read_gpw_file(**parameters):
    """ Reads data from GPW GeoTiff file and cutsout the data for the
        according country.

    Optional parameters:
        gpw_path (str): absolute path where files are stored. Default: SYSTEM_DIR
        resolution (int): the resolution in which the data output is created.
        country_adm0 (str): Three letter country code of country to be cut out.
            No default
        country_cut_mode (int): Defines how the country is cut out:
            if 0: the country is only cut out with a bounding box
            if 1: the country is cut out along it's borders
            Default: = 1 #TODO: Unimplemented
        cut_bbox (1x4 array-like): Bounding box (ESRI type) to be cut out.
            the layout of the bounding box corresponds to the bounding box of
            the ESRI shape files and is as follows:
            [minimum longitude, minimum latitude, maximum longitude, maxmimum
             latitude]
            if country_cut_mode = 1, the cut_bbox is overwritten/ignored.
        result_mode (int): Determines whether latitude and longitude are
            delievered along with gpw data (0) or only gpw_data is returned (1)
            Default = 1.

    Returns:
        tile_temp (pandas SparseArray): GPW data
        lon (list): list with longitudinal infomation on the GPW data. Same
            dimensionality as tile_temp (only returned if result_mode=1)
        lat (list): list with latitudinal infomation on the GPW data. Same
            dimensionality as tile_temp (only returned if result_mode=1)
    """
    gpw_path = parameters.get('gpw_path', SYSTEM_DIR)
    resolution = parameters.get('resolution', 30)
    cut_bbox = parameters.get('cut_bbox')
    country_adm0 = parameters.get('country_adm0')
#    country_cut_mode = parameters.get('country_cut_mode', 1)
    result_mode = parameters.get('result_mode', 0)
#    if cut_bbox is None and not (country_adm0 is None):
#        cut_bbox = LitPop._check_bbox_country_cut_mode(country_cut_mode,\
#                                                       cut_bbox, country_adm0)
    if (cut_bbox is None) & (result_mode == 0):
    # If we don't have a bbox by now and we need one, we just use the global
        cut_bbox = np.array((-180, -90, 180, 90))
    zoom_factor = 30/resolution # Orignal resolution is arc-seconds
    try:
        fname = os.path.join(gpw_path, FILENAME_GPW)
        if not os.path.isfile(fname):
            if os.path.isfile(os.path.join(SYSTEM_DIR, 'GPW_help.pdf')):
                subprocess.Popen([os.path.join(SYSTEM_DIR, 'GPW_help.pdf')],\
                                  shell=True)
                raise FileExistsError('The file ' + str(fname) + ' could not '\
                                      + 'be found. Please download the file '\
                                      + 'first or choose a different folder. '\
                                      + 'Instructions on how to download the '\
                                      + 'file has been openend in your PDF '\
                                      + 'viewer.')
            else:
                raise FileExistsError('The file ' + str(fname) + ' could not '\
                                      + 'be found. Please download the file '\
                                      + 'first or choose a different folder. '\
                                      + 'The data can be downloaded from '\
                                      + 'http://sedac.ciesin.columbia.edu/'\
                                      + 'data/collection/gpw-v4/sets/browse')
        LOGGER.debug('Trying to import the file %s', str(fname))
        gpw_file = gdal.Open(fname)
        band1 = gpw_file.GetRasterBand(1)
        arr1 = band1.ReadAsArray()
        del band1, gpw_file
        arr1[arr1 < 0] = 0
        if arr1.shape != (17400, 43200):
            LOGGER.warning('GPW data dimensions mismatch. Actual dimensions: '\
                           + '%s x %s', str(arr1.shape[0]), str(arr1.shape[1]))
            LOGGER.warning('Expected dimensions: 17400x43200.')
        if zoom_factor != 1:
            tile_temp = nd.zoom(arr1, zoom_factor, order=1)
        else:
            tile_temp = arr1
        del arr1
        if tile_temp.ndim == 2:
            if not cut_bbox is None:
                tile_temp = _gpw_bbox_cutter(tile_temp, cut_bbox, resolution)
        else:
            LOGGER.error('Error: Matrix has an invalid number of dimensions \
                         (more than 2). Could not proceed operation.')
            raise TypeError
        tile_temp = tile_temp.reshape((tile_temp.size,), order='F')
        country_shape = LitPop._get_country_shape(country_adm0)
        check_points = LitPop._LitPop_box2coords(cut_bbox, resolution, 1)
        lat, lon, encl, mask = LitPop._shape_cutter(country_shape, resolution\
                                                    =resolution,\
                                                    return_mask=1,\
                                                    point_format=0,\
                                                    check_points\
                                                    =check_points)
        del encl
        if not len(mask) == len(tile_temp):
            LOGGER.warning('Warning: length of mask and data not equal: '\
                   + '{} and {}'.format(str(len(mask)), str(len(tile_temp))))
        tile_temp = tile_temp[mask.sp_index.indices]
        if result_mode == 1:
            return tile_temp, lat, lon

        del mask, lat, lon
        return tile_temp

    except:
        LOGGER.error('Importing the GPW population density file failed. '\
                     + 'Operation aborted.')
        raise

def _gpw_bbox_cutter(gpw_data, bbox, resolution):
    """ Crops the imported GPW data to the bounding box to reduce memory foot
        print after it has been resized to desired resolution.

    Optional parameters:
        gpw_data (array): Imported GPW data in gridded format
        bbox (array 4x1): Bounding box to which the data is cropped.
        resolution (int): The resolution in arcsec to which the data has
            been resized.

    Returns:
        gpw_data (array): Cropped GPW data
    """

    """ gpw data is 17400 rows x 43200 cols in dimension (from 85 N to 60 S in
    latitude, full longitudinal range). Hence, the bounding box can easily be
    converted to the according indices in the gpw data"""
    steps_p_res = 3600/resolution
    zoom = 30/resolution
    col_min, row_min, col_max, row_max =\
        LitPop._LitPop_coords_in_glb_grid(bbox, resolution)
    row_min, row_max = int(row_min-5*steps_p_res), int(row_max-5*steps_p_res)
    # accomodate to fact that not the whole grid is present in this dataset
    if col_max < (43200/zoom)-1:
        col_max = col_max + 1
    if row_max < (17400/zoom)-1:
        row_max = row_max + 1
    gpw_data = gpw_data[:, col_min:col_max]

    if row_min >= 0 and row_min < (17400/zoom) and row_max >= 0 and\
        row_max < (17400/zoom):
        gpw_data = gpw_data[row_min:row_max, :]
    elif row_min < 0 and row_max >= 0 and row_max < (17400/zoom):
        np.concatenate(np.zeros((abs(row_min), gpw_data.shape[1])),\
                       gpw_data[0:row_max, :])
    elif row_min < 0 and row_max < 0:
        gpw_data = np.zeros((row_max-row_min, col_max-col_min))
    elif row_min < 0 and row_max >= (17400/zoom):
        np.concatenate(np.zeros((abs(row_min), gpw_data.shape[1])), gpw_data,\
                       np.zeros((row_max-(17400/zoom)+1, gpw_data.shape[1])))
    elif row_min >= (17400/zoom):
        gpw_data = np.zeros((row_max-row_min, col_max-col_min))
    return gpw_data

def check_bounding_box(coord_list):
    """ Check if a bounding box is valid.
    PARAMETERS:
        coord_list (4x1 array): bounding box to be checked.
    OUTPUT:
        isCorrectType (boolean): True if bounding box is valid, false otehrwise
    """
    is_correct_type = True
    if coord_list.size != 4:
        is_correct_type = False
        return is_correct_type
    min_lat, min_lon, max_lat, max_lon = coord_list[0], coord_list[1],\
                                         coord_list[2], coord_list[3]
    assert max_lat < min_lat, "Maximum latitude cannot be smaller than "\
                                + "minimum latitude."
    assert max_lon < min_lon, "Maximum longitude cannot be smaller than "\
                                + "minimum longitude."
    assert min_lat < -90, "Minimum latitude cannot be smaller than -90."
    assert min_lon < -180, "Minimum longitude cannot be smaller than -180."
    assert max_lat > 90, "Maximum latitude cannot be larger than 90."
    assert max_lon > 180, "Maximum longitude cannot be larger than 180."
    return is_correct_type

def _get_box_gpw(**parameters):
    """ Reads data from GPW GeoTiff file and cuts out the data along a chosen
        bounding box.

    Optional parameters:
        gpw_path (str): absolute path where files are stored.
            Default: SYSTEM_DIR
        resolution (int): the resolution in arcsec in which the data output
            is created.
        country_cut_mode (int): Defines how the country is cut out:
            if 0: the country is only cut out with a bounding box
            if 1: the country is cut out along it's borders
            Default: = 1 #TODO: Unimplemented
        cut_bbox (1x4 array-like): Bounding box (ESRI type) to be cut out.
            the layout of the bounding box corresponds to the bounding box of
            the ESRI shape files and is as follows:
            [minimum longitude, minimum latitude, maximum longitude, maxmimum
             latitude]
            if country_cut_mode = 1, the cut_bbox is overwritten/ignored.
        return_coords (int): Determines whether latitude and longitude are
            delievered along with gpw data (0)
            or only gpw_data is returned (Default: 0)
        add_one (boolean): Determine whether the integer one is added to all
            cells to eliminate zero pixels (Default: 0) #TODO: Unimplemented

    Returns:
        tile_temp (pandas SparseArray): GPW data
        lon (list): list with longitudinal infomation on the GPW data. Same
            dimensionality as tile_temp (only returned if return_coords=1)
        lat (list): list with latitudinal infomation on the GPW data. Same
            dimensionality as tile_temp (only returned if return_coords=1)
    """
    gpw_path = parameters.get('gpw_path', SYSTEM_DIR)
    resolution = parameters.get('resolution', 30)
    cut_bbox = parameters.get('cut_bbox')
#    country_cut_mode = parameters.get('country_cut_mode', 1)
    return_coords = parameters.get('return_coords', 0)
    if (cut_bbox is None) & (return_coords == 0):
    # If we don't have any bbox by now and we need one, we just use the global
        cut_bbox = np.array((-180, -90, 180, 90))
    zoom_factor = 30/resolution # Orignal resolution is arc-seconds
    try:
        fname = os.path.join(gpw_path, FILENAME_GPW)
        if not os.path.isfile(fname):
            if os.path.isfile(os.path.join(SYSTEM_DIR, 'GPW_help.pdf')):
                subprocess.Popen([os.path.join(SYSTEM_DIR, 'GPW_help.pdf')],\
                                  shell=True)
                raise FileExistsError('The file ' + str(fname) + ' could not '\
                                      + 'be found. Please download the file '\
                                      + 'first or choose a different folder. '\
                                      + 'Instructions on how to download the '\
                                      + 'file has been openend in your PDF '\
                                      + 'viewer.')
            else:
                raise FileExistsError('The file ' + str(fname) + ' could not '\
                                      + 'be found. Please download the file '\
                                      + 'first or choose a different folder. '\
                                      + 'The data can be downloaded from '\
                                      + 'http://sedac.ciesin.columbia.edu/'\
                                      + 'data/collection/gpw-v4/sets/browse')
        LOGGER.debug('Trying to import the file %s', str(fname))
        gpw_file = gdal.Open(fname)
        band1 = gpw_file.GetRasterBand(1)
        arr1 = band1.ReadAsArray()
        del band1, gpw_file
        arr1[arr1 < 0] = 0
        if arr1.shape != (17400, 43200):
            LOGGER.warning('GPW data dimensions mismatch. Actual dimensions: '\
                           + '%s x %s', str(arr1.shape[0]), str(arr1.shape[1]))
            LOGGER.warning('Expected dimensions: 17400x43200.')
        if zoom_factor != 1:
            tile_temp = nd.zoom(arr1, zoom_factor, order=1)
        else:
            tile_temp = arr1
        del arr1
        if tile_temp.ndim == 2:
            if not cut_bbox is None:
                tile_temp = _gpw_bbox_cutter(tile_temp, cut_bbox, resolution)
        else:
            LOGGER.error('Error: Matrix has an invalid number of dimensions \
                         (more than 2). Could not continue operation.')
            raise TypeError
        tile_temp = pd.SparseArray(tile_temp.reshape((tile_temp.size,),\
                                   order='F'), fill_value=0)
        if return_coords == 1:
            lon = tuple((cut_bbox[0], 1/(3600/resolution)))
            lat = tuple((cut_bbox[1], 1/(3600/resolution)))
            return tile_temp, lon, lat

        return tile_temp

    except:
        LOGGER.error('Importing the GPW population density file failed.')
        raise

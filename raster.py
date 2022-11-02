import rasterio as rio
from osgeo import gdal, ogr, osr
import os
import numpy as np
import subprocess
from multiprocessing.dummy import Pool
from functools import partial


def create_name_list(file_path):
    rasters = []
    desampled = []
    unmerged = []

    for root, dirs, files in os.walk(file_path):
        for file in files:
            if file.endswith('.asc'):
                rasters.append(file)

    for name in rasters:
        file_name = name.split('.')[0]
        desampled.append(f'{file_name}.tif')
        unmerged.append(f'{file_name}.shp')

    return rasters, desampled, unmerged


def command_list(rasters, desampled, unmerged):
    preprocess_list = []
    polygonise_list = []
    compression = '-co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9'
    desample_params = '-t_srs EPSG:4326 -dstnodata 0.0 -tr 0.05 0.05 -r max -of GTIFF'


    for input_r, output_r, output_p in zip(rasters, desampled, unmerged):
        preprocess_list.append(f'gdalwarp {desample_params} {compression} {input_r} {output_r}')
        polygonise_list.append(f'gdal_polygonize.py {output_r} -b 1 -f"ESRI Shapefile" {output_p} OUTPUT Taxon')

    return preprocess_list, polygonise_list


rasters, desampled, unmerged = create_name_list(r'F:\GISFiles\test')
preprocess, polygonise = command_list(rasters, desampled, unmerged)

# processes = [subprocess.Popen(cmd, shell=True) for cmd in to_process]
# for p in processes: p.wait()

def convert_to_polygon(file_path, preprocess, polygonise):
    pool = Pool(6)

    for i, returncode in enumerate(pool.imap(partial(subprocess.call, shell=True, cwd=fr'{file_path}'), preprocess)):
        if returncode != 0:
            print('%d command failed: %d' % (i, returncode))

    for i, returncode in enumerate(pool.imap(partial(subprocess.call, shell=True, cwd=fr'{file_path}'), polygonise)):
        if returncode != 0:
            print('%d command failed: %d' % (i, returncode))


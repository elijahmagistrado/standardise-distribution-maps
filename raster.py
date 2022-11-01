import rasterio as rio
from osgeo import gdal, ogr, osr
import os
import numpy as np
import subprocess
from multiprocessing.dummy import Pool
from functools import partial


def create_name_list(file_path):
    name_list = []
    input_names = []
    output_rasters = []
    output_polygons = []
    merged_polygons = []

    for root, dirs, files in os.walk(file_path):
        for file in files:
            if file.endswith('.asc'):
                name_list.append(file)
                input_names.append(os.path.join(root, file))

    for name in name_list:
        file_name = name.split('.')[0]
        output_rasters.append(f'{file_path}\\{file_name}.tif')
        output_polygons.append(f'{file_path}\\{file_name}.shp')
        merged_polygons.append(f'{file_path}\\{file_name}Merged.shp')
    return input_names, output_rasters, output_polygons, merged_polygons


def command_list(input_names, output_rasters, output_polygons, merged_polygons):
    preprocess_list = []
    polygonise_list = []
    merge_list = []
    compression = '-co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9'
    desample_params = '-t_srs EPSG:4326 -dstnodata 0.0 -tr 0.05 0.05 -r max -of GTIFF'
    merge_params = '-geomfield geometry -dialect SQLite'

    for input_r, output_r, output_p, merged_p in zip(input_names, output_rasters, output_polygons, merged_polygons):
        preprocess_list.append(f'gdalwarp {desample_params} {compression} {input_r} {output_r}')
        polygonise_list.append(f'gdal_polygonize.py {output_r} -b 1 -f"ESRI Shapefile" {output_p} a geometry')
        merge_list.append(f'ogr2ogr {merge_params} -sql "select st_union(GEOMETRY) as geometry from {output_p.split(".")[0]}" {merged_p} {output_p}')

    return preprocess_list, polygonise_list, merge_list


input_names, output_rasters, output_polygons, merged_polygons = create_name_list('F:\GISFiles\Crustaceans')
preprocess, polygonise, merged = command_list(input_names, output_rasters, output_polygons, merged_polygons)

# processes = [subprocess.Popen(cmd, shell=True) for cmd in to_process]
# for p in processes: p.wait()

# pool = Pool(6)
#
# for i, returncode in enumerate(pool.imap(partial(subprocess.call, shell=True), to_process)):
#     if returncode != 0:
#         print('%d command failed: %d' % (i, returncode))

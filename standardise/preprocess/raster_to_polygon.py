import os
import subprocess
from concurrent.futures import ThreadPoolExecutor


def polygonise(file_path):
    # Creates the list of file names from directory to be used in the commands below
    # Detects rasters in the ESRI ASCII (.asc) format
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

    # Generates a list of commands to be executed in subprocess threads
    preprocess_list = []  # List of gdalwarp commands
    polygonise_list = []  # List of gdal_polygonize.py commands

    # Compression parameter used to reduce file size significantly
    compression = '-co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9'

    # Parameters used to desample images to a resolution of 0.05 degrees (~5.56 km)
    # 'Maximum' resampling method used to indicate presence/absence in a given pixel
    # Also sets the correct CRS (WGS 84)
    desample_params = '-t_srs EPSG:4326 -dstnodata 0.0 -tr 0.05 0.05 -r max -of GTIFF'

    for input_r, output_r, output_p in zip(rasters, desampled, unmerged):
        preprocess_list.append(f'gdalwarp {desample_params} {compression} {input_r} {output_r}')
        polygonise_list.append(f'gdal_polygonize.py {output_r} -b 1 -f"ESRI Shapefile" {output_p} OUTPUT Taxon')

    # Executes one command for each available thread simultaneously
    def send_command(cmd):
        subprocess.run(cmd, cwd=fr'{file_path}', shell=True)

    with ThreadPoolExecutor() as executor:

        # Executing gdalwarp commands
        # Outputs GeoTiff (.tif) file
        for command in preprocess_list:
            executor.submit(send_command, command)

        # Executes gdal_polygonize.py commands
        # Outputs a single ESRI shapefile (.shp) with separate parts
        for command in polygonise_list:
            executor.submit(send_command, command)

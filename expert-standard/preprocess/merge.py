import geopandas as gpd
import pandas as pd
import os
from shapely.geometry import Polygon


def merge(file_path, sci_name, from_raster=False):
    # Merges shapefiles from file directory into layers in one shapefile
    merged = gpd.GeoDataFrame()

    # Reading all shapefiles in file path, including sub-folders
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if file.endswith('.shp'):
                # Reading shapefile into a GeoDataFrame for processing
                sf = gpd.read_file(os.path.join(root, file))

                # Some preprocessing done to clean up polygonised raster files
                if from_raster:
                    # Removal of small parts of polygons (including holes)
                    sf = remove_small_parts(sf, sci_name)

                    # Adding scientific name of species to the taxon column
                    sf[sci_name] = file.split('_currentF.shp')[0].replace('_', ' ')

                # Reprojecting to WGS 84 to ensure standardisation
                sf = sf.to_crs(epsg=4326)

                # Compiling shapefiles into one
                merged = pd.concat([merged, sf])

    # Grouping polygons of the same taxon to a multipolygon
    merged = merged.dissolve(by=sci_name, as_index=False)

    # Simplifying the snapefile to 0.05 degrees (~5.56 km) precision
    merged['geometry'] = merged.simplify(0.05)

    return merged


def remove_small_parts(polygon, sci_name):
    # Used to clean up polygonised raster files
    list_parts = []

    # Filtering out holes less than 0.003 degrees in area (equivalent to one pixel in the raster)
    for polygon in polygon.geometry:
        list_interiors = []

        for interior in polygon.interiors:
            p = Polygon(interior)
            if p.area > 0.003:
                list_interiors.append(interior)

        # New polygon without the small holes
        temp_pol = Polygon(polygon.exterior.coords, holes=list_interiors)
        list_parts.append(temp_pol)

    new_mp = gpd.GeoSeries(list_parts)

    # Filtering out polygons less than 0.006 degrees in area (equivalent to two pixels in the raster)
    big_polygons = []

    for polygon in new_mp:
        if polygon.area > 0.006:
            big_polygons.append(polygon)

    # Creating new GeoDataFrame with the cleaned up polygons and setting correct CRS
    cleaned = gpd.GeoDataFrame(columns=[sci_name], geometry=big_polygons, crs='EPSG:4326')

    return cleaned


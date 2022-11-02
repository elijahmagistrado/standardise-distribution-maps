import geopandas as gpd
import pandas as pd
import os


# Combines multiple shapefiles into one
def merge(file_path, sci_name, converted=bool, dist_type=None, current=None):
    merged = gpd.GeoDataFrame()

    # Reading all shapefiles in file path, including sub-folders
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if file.endswith('.shp'):
                sf = gpd.read_file(os.path.join(root, file))

                if converted:
                    sf = sf.dissolve(by=sci_name, as_index=False)
                    sf[sci_name] = sf[sci_name].replace(1, file.split('_currentF.shp')[0].replace('_', ' '))

                if dist_type is not None:
                    sf = sf.loc[sf[f'{dist_type}'] == f'{current}']
                sf = sf.to_crs(epsg=4326)  # Reproject to WGS84

                merged = pd.concat([merged, sf])



    # Grouping polygons of the same taxon to a multipolygon
    merged = merged.dissolve(by=sci_name, as_index=False)

    return merged

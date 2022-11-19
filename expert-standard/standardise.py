from preprocess import merge, name_match, assemble

def polygonise(file_path):
    # Polygonises all ESRI ASCII (.asc) rasters in supplied file directory
    rasters, desampled, unmerged = create_name_list(file_path)
    preprocess_list, polygonise_list = command_list(rasters, desampled, unmerged)
    convert_to_polygon(file_path, preprocess_list, polygonise_list)


def standardise_shp(file_path, sci_name, spcode, from_raster=False):
    # Standardises and merges shapefiles present in supplied file directory

    # sci_name = (str) Name of column containing the scientific names of the species
    # spcode = (int) Unique id number to add sequentially to each layer
    # from_raster = (bool) True means the shapefiles were converted from rasters using the from_raster function

    merged = merge(file_path, sci_name, from_raster)
    valid_records, family_list = name_match(merged, sci_name)
    standard = assemble(sci_name, valid_records, family_list, spcode)

    return standard


def export_shp(gdf, file_name):
    # Exports GeoDataFrame into shapefile
    # file_name should include directory + name + .shp
    gdf.to_file(file_name)

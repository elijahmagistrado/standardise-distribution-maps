from preprocess import polygonise, merge, name_match, assemble


def standardise_shp(file_path, sci_name, spcode, from_raster=False):

    if from_raster:
        polygonise(file_path)

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

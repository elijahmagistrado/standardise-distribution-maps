from .preprocess import polygonise, merge, name_match, assemble


def standardise_shp(file_path: str, sci_name: str, spcode: int, from_raster=False):
    # Standardises and merges shapefiles present in supplied file directory
    if from_raster:
        polygonise(file_path)

    merged = merge(file_path, sci_name, from_raster)
    valid_records, family_list = name_match(merged, sci_name)
    standard = assemble(sci_name, valid_records, family_list, spcode)

    return standard


def export_shp(gdf, file_name: str):
    # Exports GeoDataFrame into shapefile
    # file_name should include directory + name + .shp
    gdf.to_file(file_name)

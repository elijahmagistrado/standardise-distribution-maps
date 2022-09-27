import pandas as pd
import requests
import geopandas as gpd


def expert_std(gdf, sci_name):
    # Creating empty data frame
    standard_gdf = gpd.GeoDataFrame(
        {c: pd.Series(dtype=t)
         for c, t in {
             "gid": "int",
             "spcode": "int",
             "scientific": "str",
             "authority_": "str",
             "common_nam": "str",
             "family": "str",
             "genus_name": "str",
             "specific_n": "str",
             "min_depth": "int",
             "max_depth": "int",
             "pelagic_fl": "int",
             "estuarine_fl": "bool",
             "coastal_fl": "bool",
             "desmersal_fl": "bool",
             "metadata_u": "str",
             "wmsurl": "str",
             "lsid": "str",
             "family_lsid": "str",
             "genus_lsid": "str",
             "caab_species_number": "str",
             "caab_family_number": "str",
             "the_geom": "str",
             "area_name": "str",
             "pid": "str",
             "type": "str",
             "area_km": "float",
             "notes": "str",
             "geom_idx": "int",
             "group_name": "str",
             "genus_exemplar": "bool",
             "family_exemplar": "bool",
             "data_resource_uid": "str",
             "image_quality": "str",
             "bounding_box": "str",
             "endemic": "bool",
             "the_geom_orig": "str"
         }.items()
         }
    )
    # Setting active geometry column
    standard_gdf = standard_gdf.set_geometry("the_geom")

    # Name matching records with API
    class_api = "https://namematching-ws.ala.org.au/api/searchByClassification"
    invalid_records = []
    bad_match = []
    family_list = []
    for index, row in gdf.iterrows():
        species = requests.get(class_api, params={'scientificName': f'{row[f"{sci_name}"]}'})
        match = species.json()

        if not match['success']:
            invalid_records.append(row[f"{sci_name}"])

        else:
            if match['matchType'] != 'exactMatch' and match['matchType'] != 'canonicalMatch':
                bad_match.append(row[f"{sci_name}"])
            else:
                family_list.append(match['family'].upper())

    # Creating geoDataFrame with only valid records
    if len(invalid_records) > 0 or len(bad_match) > 0:
        expert_valid = gdf[~gdf[f"{sci_name}"].isin(invalid_records or bad_match)]
        print(f'{len(bad_match) + len(invalid_records)} low quality records have been removed from the data.')
    else:
        print('All records are valid and have good matches.')
        expert_valid = gdf

    # Splitting scientific name into its
    expert_valid[['Genus', 'Species', 'Subspecies']] = expert_valid[f"{sci_name}"].str.split(' ', n=2, expand=True)

    # Moving values from expert dataset into appropriate columns
    standard_gdf["spcode"] = range(30001, 30001 + len(expert_valid))  # fllling in dataframe with unique SPCODE > 30000
    standard_gdf["type"] = "e"  # for 'expert'
    standard_gdf["scientific"] = expert_valid[f"{sci_name}"]
    standard_gdf["family"] = family_list
    standard_gdf["the_geom"] = expert_valid["geometry"]
    standard_gdf["area_km"] = expert_valid["SHAPE_Area"]
    standard_gdf["genus_name"] = expert_valid["Genus"]

    # Output shapefile
    standard_gdf.to_file("standardised.shp")
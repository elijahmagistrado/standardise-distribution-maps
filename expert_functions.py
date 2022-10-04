import pandas as pd
import requests
import geopandas as gpd

# Creating empty data frame template
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

def vector_standard(gdf, sci_name_column, data_resource_uid):
    # Name matching records with API
    class_api = "https://namematching-ws.ala.org.au/api/searchByClassification"
    invalid_records = []
    family_list = []

    for index, row in gdf.iterrows():
        species = requests.get(class_api, params={'scientificName': f'{row[f"{sci_name_column}"]}'})
        match = species.json()

        if not match['success']:
            invalid_records.append(row[f"{sci_name_column}"])

        else:
            if match['matchType'] != 'exactMatch' and match['matchType'] != 'canonicalMatch':
                invalid_records.append(row[f"{sci_name_column}"])
            else:
                family_list.append(match['family'].upper())

    # Creating geoDataFrame with only valid records
    if len(invalid_records) > 0:
        valid_records = gdf[~gdf[f"{sci_name_column}"].isin(invalid_records)]
        print(f'{len(invalid_records)} low quality records have been removed from the data.')
    else:
        print('All records are valid and have good matches.')
        valid_records = gdf

    # Splitting scientific name into its components
    valid_records[['Genus', 'Species', 'Subspecies']] = valid_records[f"{sci_name_column}"].str.split(' ', n=2,
                                                                                                    expand=True)

    # Moving values from expert dataset into appropriate columns
    standard_gdf["spcode"] = range(30001, 30001 + len(valid_records))  # unique SPCODE > 30000
    standard_gdf["type"] = "e"  # for 'expert'
    standard_gdf["scientific"] = valid_records[f"{sci_name_column}"]
    standard_gdf["family"] = family_list
    standard_gdf["the_geom"] = valid_records["geometry"]
    standard_gdf["genus_name"] = valid_records["Genus"]
    standard_gdf["data_resource_uid"] = f"{data_resource_uid}"

    # Return value of shapefile
    return standard_gdf

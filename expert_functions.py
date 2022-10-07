import pandas as pd
import requests
import geopandas as gpd
import glob
import os


class ExpertDistMap:

    def __init__(self, file_path, sci_name_column, druid):
        self.sci_name = sci_name_column
        self.druid = druid
        self.invalid_records = []
        self.family_list = []
        self.file_path = file_path

    def compile(self):

        merged = gpd.GeoDataFrame()
        os.chdir(self.file_path)

        for root, dirs, files in os.walk(self.file_path):
            for file in files:
                if file.endswith('.shp'):
                    sf = gpd.read_file(os.path.join(root, file))
                    merged = merged.append(sf)

        print(merged)
        return merged

    def simplify(self):
        # simple = gpd.GeoDataFrame.simplify(self.gdf, 1)

    def name_match(self):
        # Name matching records with API
        class_api = "https://namematching-ws.ala.org.au/api/searchByClassification"

        for index, row in self.gdf.iterrows():
            species = requests.get(class_api, params={'scientificName': f'{row[f"{self.sci_name}"]}'})
            match = species.json()

            if not match['success']:
                self.invalid_records.append(row[f"{self.sci_name}"])

            else:
                if match['matchType'] != 'exactMatch' and match['matchType'] != 'canonicalMatch':
                    self.invalid_records.append(row[f"{self.sci_name}"])
                else:
                    self.family_list.append(match['family'].upper())

    def polygon_standard(self):
        # Calling name-matching function first
        ExpertDistMap.compile(self)
        ExpertDistMap.name_match(self)
        # Creating geoDataFrame with only valid records
        if len(self.invalid_records) > 0:
            valid_records = self[~self[f"{self.sci_name}"].isin(self.invalid_records)]
            print(f'{len(self.invalid_records)} low quality records have been removed from the data.')
        else:
            print('All records are valid and have good matches.')
            valid_records = self

        # Splitting scientific name into its components
        valid_records[['Genus', 'Species', 'Subspecies']] = valid_records[f"{self.sci_name}"].str.split(' ', n=2,
                                                                                                        expand=True)
        # Moving values from expert dataset into appropriate columns
        standard = ExpertDistMap.template

        standard["spcode"] = range(30001, 30001 + len(valid_records))  # unique SPCODE > 30000
        standard["type"] = "e"  # for 'expert'
        standard["scientific"] = valid_records[f"{self.sci_name}"]
        standard["family"] = self.family_list
        standard["the_geom"] = valid_records["geometry"]
        standard["genus_name"] = valid_records["Genus"]
        standard["data_resource_uid"] = f"{self.druid}"

        # Return value of shapefile
        return standard

    # Creating empty data frame template
    template = gpd.GeoDataFrame(
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
    template = template.set_geometry("the_geom")


test_1 = ExpertDistMap("/Users/elijah/PycharmProjects/expert-standard/Shapefile", "Taxon", "dr19999")
compiled = test_1.compile()
# test_subset = test_shp.head(20)
# test_std = ExpertDistMap(test_subset, "SCI_NAME", "dr19917")
# test_std.polygon_standard()

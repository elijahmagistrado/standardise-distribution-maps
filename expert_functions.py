import pandas as pd
import requests
import geopandas as gpd
import glob
import os


class ExpertDistMap:

    def __init__(self, file_path, sci_name_column, druid, dist_type_col=None, current_range=None):
        self.file_path = file_path
        self.sci_name = sci_name_column
        self.druid = druid
        self.dist_type_col = dist_type_col if dist_type_col is not None else None
        self.current_range = current_range if current_range is not None else None

        self.invalid_records = []
        self.family_list = []
        self.merged = None
        self.standard = None

    def compile(self):
        # Combines multiple shapefiles into one
        merged = gpd.GeoDataFrame()
        os.chdir(self.file_path)

        # Reading all shapefiles in file path, including sub-folders
        for root, dirs, files in os.walk(self.file_path):
            for file in files:
                if file.endswith('.shp'):
                    sf = gpd.read_file(os.path.join(root, file))
                    if sf[f'{self.dist_type_col}'] is not None:
                        sf = sf.loc[sf[f'{self.dist_type_col}'] == f'{self.current_range}']
                    sf = sf.to_crs(epsg=3857)
                    merged = merged.append(sf)

        # Grouping polygons of the same taxon to a multipolygon
        merged = merged.dissolve(by=f'{self.sci_name}', as_index=False)
        self.merged = merged.set_crs(epsg=3857)

    # def simplify(self):
    #     # simple = gpd.GeoDataFrame.simplify(self.gdf, 1)

    def name_match(self):
        # Name matching records with API
        class_api = "https://namematching-ws.ala.org.au/api/searchByClassification"

        for index, row in self.merged.iterrows():
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
        # Used to standardise vector data

        # Combining all shapefiles and name-matching first
        ExpertDistMap.compile(self)
        ExpertDistMap.name_match(self)

        # Creating geoDataFrame with only valid records
        if len(self.invalid_records) > 0:
            valid_records = self.merged[~self.merged[f"{self.sci_name}"].isin(self.invalid_records)]
            print(f'{len(self.invalid_records)} low quality records have been removed from the data.')
        else:
            print('All records are valid and have good matches.')
            valid_records = self.merged

        # Splitting scientific name into its components
        valid_records['Genus'] = valid_records[f"{self.sci_name}"].str.split(" ", expand=True)[0]
        valid_records['Species'] = valid_records[f"{self.sci_name}"].str.split(" ", expand=True)[1]

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
        self.standard = standard

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

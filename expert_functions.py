import pandas as pd
import requests
import geopandas as gpd
import os


class ExpertDistMap:

    def __init__(self, file_path, sci_name_column, dist_type=None, current=None):
        self.file_path = file_path
        self.sci_name = sci_name_column
        self.dist_type = dist_type if dist_type is not None else None
        self.current = current if current is not None else None

        self.invalid_records = []
        self.family_list = []
        self.common_names = []
        self.valid_records = None
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
                    if sf[f'{self.dist_type}'] is not None:
                        sf = sf.loc[sf[f'{self.dist_type}'] == f'{self.current}']
                    sf = sf.to_crs(epsg=4326)  # Reproject to WGS84
                    merged = pd.concat([merged, sf])

        # Grouping polygons of the same taxon to a multipolygon
        self.merged = merged.dissolve(by=f'{self.sci_name}', as_index=False)

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

        # Creating geoDataFrame with only valid records
        if len(self.invalid_records) > 0:
            valid_records = self.merged[~self.merged[f"{self.sci_name}"].isin(self.invalid_records)]
            print(f'{len(self.invalid_records)} low quality records have been removed from the data.')
        else:
            print('All records are valid and have good matches.')
            valid_records = self.merged

        valid_records.reset_index(drop=True)
        # Splitting scientific name into its components
        valid_records['Genus'] = valid_records[f"{self.sci_name}"].str.split(" ", expand=True)[0]
        valid_records['Species'] = valid_records[f"{self.sci_name}"].str.split(" ", expand=True)[1]

        self.valid_records = valid_records

    def assemble(self):
        # Moving values from expert dataset into appropriate columns
        standard = ExpertDistMap.template

        standard["spcode"] = range(30001, 30001 + len(self.valid_records))  # unique SPCODE > 30000
        standard["type"] = "e"  # for 'expert'
        standard["scientific"] = self.valid_records[f"{self.sci_name}"]
        standard["family"] = self.family_list
        standard["the_geom"] = self.valid_records["geometry"]
        standard["genus_name"] = self.valid_records["Genus"]
        standard["specific_n"] = self.valid_records['Species']

        # Setting final shapefile to correct CRS
        self.standard = standard.set_crs(epsg=4326)

    def polygon_standard(self, file_name):
        ExpertDistMap.compile(self)
        ExpertDistMap.name_match(self)
        ExpertDistMap.assemble(self)
        self.standard.to_file(f'{file_name}')

    # Creating empty data frame template
    template = gpd.GeoDataFrame(
        {c: pd.Series(dtype=t)
         for c, t in {
             "spcode": "int",
             "scientific": "str",
             "common_nam": "str",
             "family": "str",
             "genus_name": "str",
             "specific_n": "str",
             "the_geom": "str",
             "type": "str"
         }.items()
         }
    )

    # Setting active geometry column
    template = template.set_geometry("the_geom")

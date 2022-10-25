import pandas as pd
import requests
import geopandas as gpd
import os
from concurrent.futures import ThreadPoolExecutor, as_completed


class ExpertDistMap:

    def __init__(self, file_path, sci_name_column, dist_type=None, current=None):
        self.file_path = file_path
        self.sci_name = sci_name_column
        self.dist_type = dist_type if dist_type is not None else None
        self.current = current if current is not None else None

        self.invalid_records = []
        self.family_list = []
        self.common_names = []
        self.valid_records = []
        self.merged = gpd.GeoDataFrame()
        self.standard = gpd.GeoDataFrame()

    def merge(self):
        # Combines multiple shapefiles into one
        merged = gpd.GeoDataFrame()
        os.chdir(self.file_path)

        # Reading all shapefiles in file path, including sub-folders
        for root, dirs, files in os.walk(self.file_path):
            for file in files:
                if file.endswith('.shp'):
                    sf = gpd.read_file(os.path.join(root, file))
                    if self.dist_type is not None:
                        sf = sf.loc[sf[f'{self.dist_type}'] == f'{self.current}']
                    sf = sf.to_crs(epsg=4326)  # Reproject to WGS84
                    merged = pd.concat([merged, sf])

        # Grouping polygons of the same taxon to a multipolygon
        self.merged = merged.dissolve(by=f'{self.sci_name}', as_index=False)

    # def simplify(self):
    #     polygons = self.merged['geometry']
    #
    #     for multipolygon in polygons:
    #         polygons = list(multipolygon)
    #         for polygon in polygons:
    #
    #         pass
    #         # polygon.simplify(0.01)
    #         # polygon.nlargest(10, "first")
    #
    #     pass

    def name_match(self):
        # Name matching records with API
        class_api = "https://namematching-ws.ala.org.au/api/searchByClassification"
        name_list = self.merged[f'{self.sci_name}'].tolist()

        def make_request(name):
            with requests.get(class_api, params={'scientificName': {name}}) as match:
                return match.json(), name

        with ThreadPoolExecutor() as executor:
            good_matches = []
            futures = {executor.submit(make_request, name): name for name in name_list}
            for future in as_completed(futures):
                result = future.result()
                data = result[0]
                name = result[1]
                if data['success']:
                    if data['matchType'] == 'exactMatch' or data['matchType'] == 'canonicalMatch':
                        if data['rank'] == 'species' or data['rank'] == 'subspecies':
                            good_matches.append(name)
                            self.family_list.append(data['family'].upper())

        if len(self.merged) != len(good_matches):
            valid_records = self.merged[self.merged[f'{self.sci_name}'].isin(good_matches)].reset_index(drop=True)
            invalid_records = self.merged[~self.merged[f'{self.sci_name}'].isin(good_matches)].reset_index(drop=True)
            print(f'{len(invalid_records)} low quality record(s) removed')
            self.valid_records = valid_records
        else:
            self.valid_records = self.merged
        pass

    def assemble(self):

        # Moving values from expert dataset into appropriate columns
        standard = ExpertDistMap.template

        standard["spcode"] = range(30001, 30001 + len(self.valid_records))  # unique SPCODE > 30000
        standard["type"] = "e"  # for 'expert'
        standard["scientific"] = self.valid_records[f'{self.sci_name}']
        standard["family"] = self.family_list
        standard["the_geom"] = self.valid_records["geometry"]

        standard["genus_name"] = standard["scientific"].str.split(" ", expand=True)[0]
        standard["specific_n"] = standard["scientific"].str.split(" ", expand=True)[1]

        # Setting final shapefile to correct CRS
        self.standard = standard

    def polygon_standard(self, file_name):
        ExpertDistMap.merge(self)
        # ExpertDistMap.simplify(self)
        ExpertDistMap.name_match(self)
        ExpertDistMap.assemble(self)
        self.standard.to_file(f'{file_name}')

    # Creating empty data frame template
    template = gpd.GeoDataFrame(
        {c: pd.Series(dtype=t)
         for c, t in {
             "spcode": "int",
             "scientific": "str",
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

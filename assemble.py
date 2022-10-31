import geopandas as gpd
import pandas as pd


def assemble(sci_name, valid_records, family_list):
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

    # Moving values from expert dataset into appropriate columns
    standard = template

    standard["spcode"] = range(30001, 30001 + len(valid_records))  # unique SPCODE > 30000
    standard["type"] = "e"  # for 'expert'
    standard["scientific"] = valid_records[f'{sci_name}']
    standard["family"] = family_list
    standard["the_geom"] = valid_records["geometry"]

    standard["genus_name"] = standard["scientific"].str.split(" ", expand=True)[0]
    standard["specific_n"] = standard["scientific"].str.split(" ", expand=True)[1]

    return standard
from concurrent.futures import ThreadPoolExecutor
import geopandas as gpd
import pandas as pd


def simplify(merged):
    b = merged.geometry
    # processed = gpd.GeoSeries()

    c = b.simplify(0.05)
    merged.geometry = c
    return merged
    # for multipolygon in b:
    #     def simple(polygon):
    #         with polygon.simplify(0.01) as simplified:
    #             return simplified
    #
    #     with ThreadPoolExecutor as executor:
    #         futures = {executor.submit(simple, polygon): polygon for polygon in multipolygon}
    #         for future in futures:
    #             a = future.result()
    #             processed = pd.concat([processed, a])
        # for polygon in polygons:

        # polygon.simplify(0.01)
        # polygon.nlargest(10, "first")
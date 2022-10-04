# expert-standard
# Overview
Standardising expert distribution shapefiles before uploading into the ALA.

## Dependencies
Requires geopandas and all of its dependencies.

## Usage
`vector_standard()` is used to standardise vector shapefiles (i.e. polygons, multipolygons). It returns the standardised shapefiles which can be stored in a variable that can be exported using `geopandas.to_file()`. 

The function has three parameters:
* `gdf` : `geoDataFrame`
  * the shapefiles imported through `geopandas.read_file()`
* `sci_name_column` : `str`
  * the name of the column containing scientific names
* `data_resource_uid` : `str`
  * the unique ID of the data resource it is going to be placed under

### Example

```
import geopandas as gpd

expert_data = gpd.read_file("distribution.shp")
standardised_data = vector_standard(expert_data, "scientific_name", "dr10000")
standardised_data.to_file("expert_standardised.shp")
```


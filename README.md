# standardise-distribution-maps
## Overview
Used for standardising expert distribution maps to be added to the ALA spatial services. This package contains 
functions to process both raster and vector data. The final output is a single ESRI shapefile `.shp` and its associated 
files `.cpg .dbf .prj .shx` containing layers of distribution maps of species present in the ALA. The shapefile (and all 
of its components) must be compressed into a `.zip` file before uploading. 

## Dependencies
This package requires the following python packages to function:
* `geopandas` (and all of its dependencies)
* `dask-geopandas`
* `aiohttp`

## Preparing data for input
The file uploaded to the ALA spatial service requires a single shapefile containing layers of distribution maps for each
species. For the functions to work, the data has some requirements to work:
* The file names must contain the binomial scientific name of the species **OR** there must be a column on the shapefile's 
attribute table containing the scientific name.
  * Correct: `Vombatus_ursinus.shp`, `Vombatus ursinus.shp`
  * Also correct: `Distribution_maps.shp` with column name `Taxon` that contains scientific names
* All files must be in the same directory. **Files in subfolders will not be read**
* Rasters must be in ESRI ASCII (.asc) format.
* Shapefiles must be ESRI shapefile (.shp) format.


## Standardising shapefiles
The shapefile must be transformed to match a specific format to be processed correctly in the spatial service.

### standardise_shp(file_path, sci_name, spcode, from_raster=False)

`standardise_shp()` merges, reprojects, name matches, and filters all valid records into a single GeoDataFrame. Can also 
clean up polygonised raster files by removing small holes and polygons that will not be visible in the final images.

**Parameters:**
* **file_path : str**
  * File directory containing the shapefiles.
* **sci_name : str**
  * Name of the column containing scientific names.
* **spcode : int**
  * Unique id that is sequentially added to each geometry layer. Must be greater than 30000
* **from_raster : bool**
  * Default value is `False`
  * `True` if shapefiles are the polygonised rasters using the `from_raster()` function.
  * Calls `polygonise()` when `True`.

### export_shp(gdf, file_name)
Exports the GeoDataFrame into an ESRI shapefile (.shp)

**Parameters:**
* **gdf : GeoDataFrame**
  * Name of the object storing the GeoDataFrame created by `standardise_shp()`
* **file_name : str**
  * Destination of the shapefile including the desired file name. Must end with `.shp`

## Raster conversion
Distribution maps must be in ESRI shapefile (.shp) format. Raster distribution maps therefore must be converted into 
shapefiles before it can be standardised. 

### polygonise(file_path)

The function `polygonise()` is used to convert all ESRI ASCII (.asc) raster files into shapefiles. Outputs shapefiles in
the same directory supplied. This function is automatically called when `from_raster=True`. 

**Parameters:**

* **file_path : str**
  * File directory containing rasters



## Usage
```
from standardise import standardise_shp, export_shp


# Starting with raster files
standardised = standardise_shp(r'C:\Users\Bob\Rasters', 'Taxon', 31296, from_raster=True)
export_shp(standardised, r'C:\Users\Bob\Rasters\standardised.shp')


# Starting with shapefiles
standardised = standardise_shp(r'C:\Users\Bob\Shapefiles', 'scientific_name', 33786)
export_shp(standardised, r'C:\Users\Bob\Shapefiles\standardised.shp')
```


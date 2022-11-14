# expert-standard
Used for standardising expert distribution maps to be added to the ALA spatial services.

## Standardising shapefiles
The file uploaded to the ALA spatial service requires a single shapefile containing layers of distribution maps for each
species. 

### vector_standard(file_path, sci_name, spcode, from_raster=False)

`vector_standard` merges, name matches, and filters all valid records into a single GeoDataFrame. Can also clean up 
polygonised raster files by removing small holes and polygons that will not be visible in the final images.

**Parameters**
* **file_path : str**
  * File directory containing the shapefiles.
* **sci_name : str**
  * Name of the column containing scientific names.
* **spcode : int**
  * Unique id that is sequentially added to each geometry layer.
* **from_raster : bool**
  * Default value is `False`
  * `True` if shapefiles are the polygonised rasters using the `from_raster()` function.

### export_shp(gdf, file_name)
Exports the GeoDataFrame into an ESRI shapefile (.shp)

**Parameters**
* **gdf : GeoDataFrame**
  * Name of the object storing the GeoDataFrame created by `vector_standard()`
* **file_name : str**
  * Destination of the shapefile including the desired file name. Must end with `.shp`

## Raster conversion
Distribution maps must be in ESRI shapefile (.shp) format. Raster distribution maps must be converted into 
shapefiles before it can be standardised. 

### polygonise(file_path)

The function `polygonise()` is used to convert all ESRI ASCII (.asc) raster files into shapefiles. Outputs shapefiles in
the same directory supplied. Note that the column name containing the scientific names is called `Taxon`.

**Parameters:**

* **file_path : str**
  * File directory containing rasters

### Usage
```
from expert-standard.standardise import polygonise, vector_standard, export_shp


# Starting with raster files
polygonise(r'C:\Users\Bob\Rasters')
standardised = vector_standard(r'C:\Users\Bob\Rasters', 'Taxon', 30000, from_raster=True)
standardised.export_shp(r'C:\Users\Bob\Output\standardised.shp')


# Starting with shapefiles
standardised = vector_standard(r'C:\Users\Bob\Shapefiles', 'scientific_name', 30000)
standardised.export_shp(r'C:\Users\Bob\Output\standardised.shp')
```


# Flowcast preprocessing

This folder includes various tools used in the preprocessing pipeline used to transform data before usage in the final service.

## Watershed delineation and flow distance

### Dependencies

You need to install quite a lot for this to run:
- [GDAL](https://gdal.org/en/stable/download.html#binaries)
  - Tooling for manipulating tiff and asc raster files.
  - Ships with [QGIS](https://qgis.org/download/), which you will probably need to view outputs.
- [just](https://just.systems/)
  - Make style command runner
- [WhiteboxTools open core](https://www.whiteboxgeo.com/download-whiteboxtools/)
  - Hydrology tools
- [uv](https://docs.astral.sh/uv/getting-started/installation/) or pip

### Basic example

To download and process the department Haute-Garonne (031), run:

```bash
# Download DEM 7z
just download 031
# Extract, merge and fix metadata
just process 031

just merge data/031/dem.tiff data/dem-dep-031/*
rm -rf data/dem-dep-031
```

You should now have the file data/031/dem.tiff, which is an elevation map of the whole department.

You now need to specify the drainage point(s):
- `qgis data/031/dem.tiff`
- Locate your drainage point. Make sure it is on the dem layer.
- layer => create layer => shapefile
  - set path to data/031/points.shp
  - set it to points / multiple points
- Right click on new layer, edit
- Select the point add tool in the toolbar
- Add your point
- Right click on the layer and click save changes

Now you can calculate distances, run:
```bash
just distance-all data/031/dem.tiff data/031/points.shp
```

If all goes well, you should find the data/031/dem-dist.tiff raster with time to drainage point in seconds.
Open it in QGIS and inspect it.

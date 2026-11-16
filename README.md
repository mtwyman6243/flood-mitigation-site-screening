# Flood Retention Basin Site Selection — Carinthia, Austria

A GIS multi-criteria decision analysis (MCDA) for assessing and siting decentralized flood retention basins in southern Austria. It combines **Flood Hazard (FLH)**, **Flood Exposure (FLE)** and **Land Suitability (LSU)** submodels into a composite **Flood Mitigation Suitability (FMS)** surface, then screens and ranks candidate basin sites.

**[View the interactive webmap →](https://mtwyman6243.github.io/research.html)** · Part of [Matt Twyman's GIS portfolio](https://mtwyman6243.github.io)

## About the project

This research was carried out as a Marshall Plan Foundation Fellow (2025). It was hosted by Dr. Gernot Paulus, Department of Geoinformation and Environmental Technologies, Carinthia University of Applied Sciences (CUAS), and supervised by Dr. Douglas Stow and Dr. Piotr Jankowski of the SDSU Department of Geography.

- The three submodels were aggregated with a Weighted Linear Combination into a 1 m FMS surface.
- Candidate sites were extracted with a binary threshold and a minimum-area filter. Carrying capacity was then estimated for each site, and the sites were prioritized by rank.
- Global variance-based sensitivity and uncertainty analysis (quasi-random weight perturbation, Sobol indices) found Elevation, Land Cover Type and Soil Type to have the most influence on the rankings.
- Of 753 candidate polygons, **20 priority sites** were identified. They were ranked by storage capacity potential, rank stability and population coverage.

## What's in this repo

```
scripts/
  prepare_austria_data.py  # merges the 4 submodel GeoPackages -> one WGS84 GeoJSON
  austria_projection.py    # LCC 2SP inverse (Bessel 1841) + MGI->WGS84 Helmert shift
  gpkg_reader.py           # minimal GeoPackage reader (pure Python)
  geotiff_reader.py        # minimal GeoTIFF reader (struct + numpy)
  raster_to_web.py         # reprojects 1 m rasters to WGS84 PNG overlays for Leaflet
data/
  austria_candidate_sites.geojson  # 20 candidate sites with volume, area and submodel scores
maps/
  austria_candidate_sites_map.html # standalone Leaflet webmap
  assets/                          # raster overlays (PNG) + WGS84 bounds (JSON)
```

## Reprojecting without GDAL

The source data is in **MGI / Austria Lambert (EPSG:31287)**. pyproj wasn't available offline, so `austria_projection.py` reproduces PROJ's two-step transform by hand:

1. An inverse ellipsoidal Lambert Conformal Conic (2SP) on the Bessel 1841 ellipsoid, giving MGI geographic coordinates.
2. A 3-parameter Helmert datum shift through geocentric Cartesian coordinates, from MGI to WGS84 (EPSG transformation 1618).

## Running it

The raw inputs (GeoPackages and GeoTIFFs) aren't committed. Put them in a `raw/` folder, then:

```bash
pip install -r requirements.txt
cd scripts
python prepare_austria_data.py --uploads ../raw --output ../data/austria_candidate_sites.geojson
python raster_to_web.py --input ../raw/<FMS raster>.tif \
    --output ../maps/assets/fms_raster.png --crs austria
```

To view the map, open `maps/austria_candidate_sites_map.html` in a browser.

**Tools:** ArcGIS Pro · Python · NumPy · Leaflet · Weighted Linear Combination · Sobol sensitivity analysis

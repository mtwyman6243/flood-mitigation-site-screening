"""
prepare_austria_data.py
-------------------------
Combines the four Retention Basin submodel GeoPackage outputs (Final FMS,
Flood Exposure, Flood Hazard, Land Suitability — each a zonal-statistics
join onto the 20 filtered candidate basin sites) into a single GeoJSON,
reprojected from MGI / Austria Lambert (EPSG:31287) to WGS84.

Usage:
    python prepare_austria_data.py --uploads /path/to/gpkg/files \
        --output ../data/austria_candidate_sites.geojson
"""

import argparse
import json
import os

from gpkg_reader import read_gpkg_layer
from austria_projection import austria_lambert_to_wgs84

LAYERS = {
    "fms": "Final_FMS_Filtered_Candidate_Sites_25_12_10_07_41.gpkg",
    "flh": "FLH_Filtered_Candidate_Sites_25_12_10_07_41.gpkg",
    "fle": "FLE_Filtered_Candidate_Sites_25_12_10_07_41.gpkg",
    "lsu": "LSU_Filtered_Candidate_Sites_25_12_10_07_41.gpkg",
}


def multipolygon_to_geojson_coords(multipoly):
    return [[[[lon, lat] for lon, lat in ring] for ring in poly] for poly in multipoly]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uploads", default="../raw")
    ap.add_argument("--output", default="../data/austria_candidate_sites.geojson")
    args = ap.parse_args()

    layer_data = {}
    base_geom_by_fid = {}
    for key, fname in LAYERS.items():
        path = os.path.join(args.uploads, fname)
        feats = read_gpkg_layer(path, project_fn=austria_lambert_to_wgs84)
        by_fid = {}
        for i, (attrs, geom) in enumerate(feats):
            fid = i  # positional id; all four layers share the same 20 sites in the same order
            by_fid[fid] = attrs
            if key == "fms":
                base_geom_by_fid[fid] = geom
        layer_data[key] = by_fid

    features = []
    for fid, geom in base_geom_by_fid.items():
        fms_attrs = layer_data["fms"][fid]
        props = {
            "site_id": fid + 1,
            "cut_m3": round(fms_attrs.get("cut_m3", 0), 1),
            "fill_m3": round(fms_attrs.get("fill_m3", 0), 1),
            "net_m3": round(fms_attrs.get("net_m3", 0), 1),
            "area_m2": round(fms_attrs.get("area_m2", 0), 1),
            "ref_elev": round(fms_attrs.get("ref_elev", 0), 2),
        }
        for key in LAYERS:
            attrs = layer_data[key].get(fid, {})
            props[f"{key}_mean"] = round(attrs.get("mean", 0), 4) if attrs.get("mean") is not None else None
            props[f"{key}_rank"] = attrs.get("rank")

        features.append({
            "type": "Feature",
            "properties": props,
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": multipolygon_to_geojson_coords(geom),
            },
        })

    fc = {"type": "FeatureCollection", "features": features}
    with open(args.output, "w") as f:
        json.dump(fc, f)

    print(f"Wrote {len(features)} candidate site features to {args.output}")


if __name__ == "__main__":
    main()

# Least Cost Path Modeling

import arcpy
from arcpy.sa import *

arcpy.env.overwriteOutput = True

def LCP_Analysis(rasters, weights, source_point, destination_point, LCP_polyline_output, smoothing_tolerance):
    arcpy.CheckOutExtension("Spatial")
    
    combined_raster = None

    rasters_list = rasters.split(";")
    weights_list = weights.split(";") if weights else [1] * len(rasters_list)  # Default weights to 1 if not provided

    for raster_path, weight in zip(rasters_list, weights_list):
        raster = arcpy.Raster(raster_path) * float(weight)
        combined_raster = raster if combined_raster is None else combined_raster + raster

    combined_raster.save(output_raster)
    
    cost_distance_raster = arcpy.sa.CostDistance(source_point, combined_raster)
    cost_distance_raster.save("in_memory\\cost_distance_raster")
    backlink = arcpy.sa.CostBackLink(source_point, combined_raster)
    cost_path_raster = arcpy.sa.CostPath(destination_point, cost_distance_raster, backlink)
    arcpy.conversion.RasterToPolyline(cost_path_raster, LCP_polyline_output)
    
    arcpy.SmoothLine_cartography(LCP_polyline_output, LCP_polyline_output + "_smoothed", "PAEK", smoothing_tolerance)

    arcpy.CheckInExtension("Spatial")

if __name__ == "__main__":
    rasters = arcpy.GetParameterAsText(0)
    weights = arcpy.GetParameterAsText(1)
    output_raster = arcpy.GetParameterAsText(2)
    source_point = arcpy.GetParameterAsText(3)
    destination_point = arcpy.GetParameterAsText(4)
    LCP_polyline_output = arcpy.GetParameterAsText(5)
    smoothing_tolerance_value = arcpy.GetParameterAsText(6)
    
    smoothing_tolerance = float(smoothing_tolerance_value.split()[0])

    LCP_Analysis(rasters, weights, source_point, destination_point, LCP_polyline_output, smoothing_tolerance)

# Avoidance Raster Modeling

import arcpy
from arcpy.sa import *

arcpy.env.overwriteOutput = True

def create_feature_to_avoid_raster(input_features, buffer_distances, avoidance_raster):
    arcpy.CheckOutExtension("Spatial")

    buffered_feature_layers = []

    unit_mapping = {
        "Meters": "METERS",
        "Kilometers": "KILOMETERS",
        "Inches": "INCHES",
        "Feet": "FEET",
        "Miles": "MILES",
        "Yards": "YARDS"
        # Add other units as needed
    }

    for idx, feature in enumerate(input_features):
        buffer_distance = buffer_distances[idx].strip()
        distance, unit = buffer_distance.split()
        unit = unit.strip("'")
        unit = unit.strip()

        standard_unit = unit_mapping.get(unit)

        if standard_unit:
            numeric_distance = float(distance.strip("'"))

            buffer_output = f"in_memory\\buffered_feature_{idx}"
            arcpy.Buffer_analysis(feature, buffer_output, f"{numeric_distance} {standard_unit}")

            buffered_feature_layers.append(buffer_output)
        else:
            arcpy.AddError(f"Unsupported linear unit: {unit}")

    if len(buffered_feature_layers) > 0:
        union_output = "in_memory\\unioned_features"
        arcpy.Union_analysis(buffered_feature_layers, union_output)

        # Set buffer_value & maximum_avoidance_weight variables to the same value as maximum slope reclassification weight
        buffer_value = 100
        arcpy.FeatureToRaster_conversion(union_output, "OBJECTID", avoidance_raster, buffer_value)

        maximum_avoidance_weight = 100
        reclassified_raster = Con(~IsNull(avoidance_raster), maximum_avoidance_weight)

        reclassified_output = "in_memory\\reclassified_raster"
        reclassified_raster.save(reclassified_output)

        final_raster = Con(IsNull(reclassified_output), 0, reclassified_output)

        final_raster.save(avoidance_raster)

    arcpy.CheckInExtension("Spatial")

if __name__ == "__main__":
    input_features = arcpy.GetParameterAsText(0).split(";")
    buffer_distances = arcpy.GetParameterAsText(1).split(";")
    avoidance_raster = arcpy.GetParameterAsText(2)

    arcpy.AddMessage(f"Buffer Distances: {buffer_distances}")

    create_feature_to_avoid_raster(input_features, buffer_distances, avoidance_raster)

# Route Segmentation

import arcpy
from arcpy.sa import *
import os

arcpy.env.overwriteOutput = True

def segment_polyline_by_curvature(input_polyline, OutputSegments):
    arcpy.CheckOutExtension("Spatial")
    def extract_vertex_coordinates(polyline):
        vertices = []
        with arcpy.da.SearchCursor(polyline, ["SHAPE@"]) as cursor:
            for row in cursor:
                polyline = row[0]
                for part in polyline:
                    for pnt in part:
                        vertices.append((pnt.X, pnt.Y))
        return vertices

    def segment_polyline(polyline_vertices):
        segments = []
        for i in range(len(polyline_vertices) - 1):
            segments.append([polyline_vertices[i], polyline_vertices[i+1]])
        return segments

    vertices = extract_vertex_coordinates(input_polyline)

    segments = segment_polyline(vertices)

    arcpy.management.CreateFeatureclass(os.path.dirname(OutputSegments), os.path.basename(OutputSegments), "POLYLINE", spatial_reference=input_polyline)

    with arcpy.da.InsertCursor(OutputSegments, ["SHAPE@"]) as cursor:
        for segment in segments:
            array = arcpy.Array([arcpy.Point(x, y) for x, y in segment])
            polyline = arcpy.Polyline(array)
            cursor.insertRow([polyline])
    
    arcpy.CheckInExtension("Spatial")

if __name__ == "__main__":
    input_polyline = arcpy.GetParameterAsText(0)
    OutputSegments = arcpy.GetParameterAsText(1)

    segment_polyline_by_curvature(input_polyline, OutputSegments)


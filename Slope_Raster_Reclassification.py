# Slope Raster Modeling & Reclassification

import arcpy
from arcpy.sa import *

arcpy.env.overwriteOutput = True

def reclassify_slope(Input_Raster, Reclassified_Slope, Reclassification_Values):
    arcpy.CheckOutExtension("Spatial")
    slope_raster = Slope(Input_Raster, "DEGREE", 1, "PLANAR")
    reclassified_raster = Reclassify(slope_raster, "VALUE", Reclassification_Values, "NODATA")
    reclassified_raster.save(Reclassified_Slope)
        
    arcpy.CheckInExtension("Spatial")


if __name__ == "__main__":
    Input_Raster = arcpy.GetParameterAsText(0)
    Reclassified_Slope = arcpy.GetParameterAsText(1)
    Reclassification_Values = eval(arcpy.GetParameterAsText(2))

    reclassify_slope(Input_Raster, Reclassified_Slope, Reclassification_Values)
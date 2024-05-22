import arcpy
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf_report(polyline_feature_set, output_pdf):
    try:
        # Convert feature set to feature class in memory
        arcpy.CopyFeatures_management(polyline_feature_set, "in_memory\\temp_polyline")

        # Get the spatial reference of the polyline feature
        desc = arcpy.Describe("in_memory\\temp_polyline")
        spatial_ref = desc.spatialReference

        # Get the length of the polyline
        length = 0
        with arcpy.da.SearchCursor("in_memory\\temp_polyline", ['SHAPE@LENGTH']) as cursor:
            for row in cursor:
                length += row[0]

        # Convert length to miles if it's not already in miles
        if spatial_ref.linearUnitName == "Meter":
            length_miles = length * 0.000621371  # Convert meters to miles
        elif spatial_ref.linearUnitName == "Foot_US":
            length_miles = length / 5280  # Convert feet to miles
        else:
            # If units are not meters or feet, use as-is and indicate the units are unknown
            length_miles = length
            unit = spatial_ref.linearUnitName

        # Get the start and end coordinates
        start_coord = None
        end_coord = None
        with arcpy.da.SearchCursor("in_memory\\temp_polyline", ['SHAPE@']) as cursor:
            for row in cursor:
                if row[0]:
                    start_point = row[0].firstPoint
                    end_point = row[0].lastPoint
                    start_coord = (start_point.X, start_point.Y)
                    end_coord = (end_point.X, end_point.Y)

        # Get the coordinate reference system (CRS) information
        crs = desc.spatialReference.name if desc.spatialReference else "N/A"
        
        # Prepare data for the PDF
        report_data = [
            ["Attribute", "Value"],
            ["Length of Polyline", f"{length_miles:.2f} miles" if spatial_ref.linearUnitName in ["Meter", "Foot_US"] else f"{length} {unit}"],
            ["Start Coordinates", f"{start_coord}" if start_coord else "N/A"],
            ["End Coordinates", f"{end_coord}" if end_coord else "N/A"],
            ["Coordinate Reference System", crs]
        ]

        # Generate PDF report
        doc = SimpleDocTemplate(output_pdf, pagesize=letter)
        elements = []

        styles = getSampleStyleSheet()
        title = Paragraph("Least Cost Path Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.25 * inch))

        table = Table(report_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),  # Header background color
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # Header text color
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alignment for all cells
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
            ('FONTSIZE', (0, 0), (-1, 0), 12),  # Header font size
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding for header cells
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),  # Cell background color
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),  # Cell text color
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)  # Grid lines color
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.5 * inch))

        # Get current map view from ArcGIS Pro and save it as an image
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        layouts = aprx.listLayouts()
        arcpy.AddMessage(f"Number of layouts found: {len(layouts)}")
        if not layouts:
            elements.append(Paragraph("Layout Not Found", styles['Normal']))
        else:
            for layout in layouts:
                arcpy.AddMessage(f"Checking layout: {layout.name}")
                all_elements = layout.listElements()
                for element in all_elements:
                    arcpy.AddMessage(f"Element: {element.name} (Type: {element.type})")
                elements_map_frame = layout.listElements("MAPFRAME_ELEMENT")
                arcpy.AddMessage(f"Number of map frames found in {layout.name}: {len(elements_map_frame)}")
                if not elements_map_frame:
                    elements.append(Paragraph(f"Map Frame Not Found in layout {layout.name}", styles['Normal']))
                else:
                    map_frame = elements_map_frame[0]  # Assuming the first map frame is the one we want
                    arcpy.AddMessage(f"Using map frame: {map_frame.name}")
                    map_png_path = os.path.splitext(output_pdf)[0] + "_map_frame.png"
                    layout.exportToPNG(map_png_path, resolution=300)
                    elements.append(Paragraph("Map Layout", styles['Heading2']))
                    elements.append(Image(map_png_path, width=6*inch, height=4*inch))
                    break  # Exit after finding the first valid map frame

        doc.build(elements)

        # Check if the PDF is created successfully
        if os.path.exists(output_pdf):
            arcpy.AddMessage(f"PDF generated successfully at {output_pdf}")
        else:
            arcpy.AddError(f"Failed to generate PDF at {output_pdf}")

    except Exception as e:
        arcpy.AddError(f"Error: {str(e)}")
    finally:
        # Clean up in-memory feature class
        arcpy.Delete_management("in_memory\\temp_polyline")

if __name__ == "__main__":
    # Get input parameters from ArcGIS tool
    polyline_feature_set = arcpy.GetParameterAsText(0)
    output_pdf = arcpy.GetParameterAsText(1)

    # Generate PDF report
    generate_pdf_report(polyline_feature_set, output_pdf)
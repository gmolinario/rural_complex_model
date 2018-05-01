
####################################################################
# This script cleans the master input mask for the LFT
#	- Subtracts NF and WD from all three masks when outside of the AOI
#	- replaces the master masks
#
# GM 11/13/2014
# edited names for ROC running (04/2018)
####################################################################


####################################################################
#Import arcpy modules
import arcpy
from arcpy import env
from arcpy.sa import *
import os

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

# If you want to overwrite output files
# arcpy.env.overwriteOutput=True # careful not to overwrite files by mistake. 


####################################################################
# Global variables

# Latest LFT directory
root=r"C:\Data_Molinario\temp\LFT_local\19th_run"

# AOI files directory
aoiFolder=root+r"\AOI"

#FACET folder
facetFolder=r"C:\Data_Molinario\temp\LFT_local\19th_run\FACET_ROC"

#FACET file
facet=facetFolder+"\\"+"myfacet.tif"

outputIntermediateFolder=aoiFolder+"\\"+"final_mask_from_AOI_process"
if not os.path.exists(outputIntermediateFolder):
	os.makedirs(outputIntermediateFolder)
	print "Made "+outputIntermediateFolder+" folder."

# Insert path to raster to snap to 
tempEnvironment0 = arcpy.env.snapRaster
arcpy.env.snapRaster = r"C:\Data_Molinario\temp\LFT_local\19th_run\FACET_ROC\myfacet.tif"

# Set extent to FACET extent
arcpy.env.extent = r"C:\Data_Molinario\temp\LFT_local\19th_run\FACET_ROC\myfacet.tif"


arcpy.env.overwriteOutput=True


################################################
# Readme - process to build LFT input mask
################################################

		# 	- Make raster from polygon buffer
		#	- Reclass raster to outside AOI = 100
		# 	- Add to FACET
		#	- NF and WD outside AOI reclass to 100 else 0
		#	- Add that raster to existing master LFT masks
		#	- reclass result (100s become 0)
		#	- Overwrite existing master files

##########################################################
# Make raster from polygon AOI
##########################################################

aoiName="aoi_full"
env.workspace=aoiFolder
print env.workspace
aoiPolygon=arcpy.ListFeatureClasses("*"+aoiName+"*")[0]
print aoiPolygon
outRaster=outputIntermediateFolder+"\\"+ aoiName+".tif"
print outRaster
arcpy.env.extent = r"C:\Data_Molinario\temp\LFT_local\19th_run\FACET_ROC\myfacet.tif"
print "Output extent is same as "+ str(arcpy.env.extent) 
arcpy.env.snapRaster = r"C:\Data_Molinario\temp\LFT_local\19th_run\FACET_ROC\myfacet.tif"

# now do the conversion
arcpy.PolygonToRaster_conversion(aoiPolygon, "FID", outRaster, "CELL_CENTER","", "60")


##########################################################
# Reclass raster
##########################################################

env.workspace=outputIntermediateFolder
raster=arcpy.ListRasters("*"+aoiName+"*")[0]
print raster
reclassField = "Value"
remap=RemapValue([
	[0,0],
	["NoData",100]])
rclName=aoiName+"_rcl.tif"
outReclassify=Reclassify(raster,reclassField,remap)
outReclassify.save(rclName)


###############################################
# Add raster to FACET
###############################################

raster=arcpy.ListRasters("*"+rclName+"*")[0]
facetPlusAOI=Raster(raster)+Raster(facet)
facetPlusAoiName="facet_added_to_"+aoiName+".tif"
facetPlusAOI.save(facetPlusAoiName)


###############################################
# Reclass result into mask to subtract from masters
###############################################

raster=arcpy.ListRasters("*"+facetPlusAoiName+"*")[0]
print raster
reclassField = "Value"
remap=RemapRange([
# Outside of buffer
	[0,12,0], # All FACET within the AOI 
	# Below all outside AOI
	[100,100,0], # No data (outside DRC) inside AOI - should not exist 
	[101,101,100], # Non forest
	[102,103,0], # Water and no data 
	[104,104,100], # Woodlands
	[105,112,0]]) # All other classes outside AOI
	# WDL 2005 and 2010 is already in the masks so don't have to do anything to it. 

name=facetPlusAoiName[:-4]+"_rcl.tif"
print name
outReclassify=Reclassify(raster,reclassField,remap)
outReclassify.save(name)

################################################
# Add the NF/WD outside AOI mask to the master lft masks
################################################
# Periods of LFT 
# LFTs= ["2000","2005", "2010"]
LFTs= ["2000"]
NfWdOutAoiMask=env.workspace+"\\"+name
for lft in LFTs:
	if "2000" in lft:
		env.workspace=root+"\\"+lft+"\Master"
		master=arcpy.ListRasters()[0] # there is only one raster in that folder.
		addToMaster=Raster(master)+Raster(NfWdOutAoiMask)
		name="Master_"+lft+"_with_NfWd_ToSubtract.tif"
		env.workspace=outputIntermediateFolder
		addToMaster.save(name)
		print name 
		reclassField = "Value"
		remap=RemapValue([
		# Outside of buffer
			[0,0], # no data
			[1,1], # RC (not NF and WD outside of AOI)  
			[2,2], # forest
			[100,0], # 
			[101,0]]) # NF and WD outside of AOI should be 101 only  
		rclAddToMaster=Reclassify(addToMaster,reclassField,remap)
		outName=master[:-4]+"_wOut_extrAoi_NfWd.tif"
		rclAddToMaster.save(outName)
		print outName


	elif "2005" in lft:
		env.workspace=root+"\\"+lft+"\Master"
		master=arcpy.ListRasters()[0] # there is only one raster in that folder.
		addToMaster=Raster(master)+Raster(NfWdOutAoiMask)
		name="Master_"+lft+"_with_NfWd_ToSubtract.tif"
		env.workspace=outputIntermediateFolder
		addToMaster.save(name) 
		print name
		reclassField = "Value"
		remap=RemapValue([
		# Outside of buffer
			[0,0], # no data
			[1,1], # RC (not NF and WD outside of AOI)  
			[2,2], # forest
			[100,0], # 
			[101,0]]) # NF and WD outside of AOI should be 101 only  
		rclAddToMaster=Reclassify(addToMaster,reclassField,remap)
		outName=master[:-4]+"_wOut_extrAoi_NfWd.tif"
		rclAddToMaster.save(outName)
		print outName
	else: # 2010	
		env.workspace=root+"\\"+lft+"\Master"
		master=arcpy.ListRasters()[0] # there is only one raster in that folder.
		addToMaster=Raster(master)+Raster(NfWdOutAoiMask)
		name="Master_"+lft+"_with_NfWd_ToSubtract.tif"
		env.workspace=outputIntermediateFolder
		addToMaster.save(name)
		print name 
		reclassField = "Value"
		remap=RemapValue([
		# Outside of buffer
			[0,0], # no data
			[1,1], # RC (not NF and WD outside of AOI)  
			[2,2], # forest
			[100,0],
			[101,0]]) # NF and WD outside of AOI should be 101 only  
		rclAddToMaster=Reclassify(addToMaster,reclassField,remap)
		outName=master[:-4]+"_wOut_extrAoi_NfWd.tif"
		rclAddToMaster.save(outName)
		print outName

#######################################################
# Copy final rasters back into master folder
#######################################################


env.workspace=outputIntermediateFolder
rasters=arcpy.ListRasters("*_wOut_extrAoi_NfWd.tif*")
print rasters
for raster in rasters:
	if "2000" in raster:
		name=raster[:8]+"_final.tif"
		dst=root+"/2000/Master/"+name
		arcpy.CopyRaster_management(raster,dst,"DEFAULTS","","","","","")
	elif "2005" in raster:
		name=raster[:8]+"_final.tif"
		dst=root+"/2005/Master/"+name
		arcpy.CopyRaster_management(raster,dst,"DEFAULTS","","","","","")
	else:
		name=raster[:8]+"_final.tif"
		dst=root+"/2010/Master/"+name
		arcpy.CopyRaster_management(raster,dst,"DEFAULTS","","","","","")

# end 

# next run the build hybrid GFC mask script 





####################################################################
# This script builds the input mask for the LFT based on FACET
#
#
#	- Previously the mask was built manually and then refined with script arcpyBuildSelectionMaskForNFandWD.py
#		To filter out fragmented forest caused by small rivers and NF patches. 
#	- This mask is built on facet
# 	- Have to run this to get the baseline 2000 mask that's built on FACET, subsequent script replaces other years though. 
#
#	Version History
# GM 06/25/2014
# revision for v14
#	10/30/2014
#	11/09/2014
#	04/2018 revision for v18 - in this version run for just 2018? 
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
# arcpy.env.overwriteOutput=True

####################################################################
# Global variables

# LFT directory
root=r"C:\Data_Molinario\temp\LFT_local\19th_run"

# FACET class masks folder
facetMasks=r"C:\Data_Molinario\temp\LFT_local\19th_run\FACET_class_masks"

# Secondary forest folder
sfMaskFolder=r"C:\Data_Molinario\temp\LFT_local\19th_run\FACET_class_masks\Secondary_forest\SF_2000"

#FACET folder
facetFolder=r"C:\Data_Molinario\temp\LFT_local\19th_run\FACET_ROC"

# SF and loss masks expansions for LFT input mask building
facetMaskWorkFolder=r"SF_and_Loss_Masks_for_NF_WD_selection\\v19"
facetMaskWorkFolderPath=facetMasks+"/"+facetMaskWorkFolder

if not os.path.exists(facetMaskWorkFolderPath):
	os.makedirs(facetMaskWorkFolderPath)
	print "Made "+facetMaskWorkFolder+" folder."

# if needed, if I don't rebuild from scratch. 
# Raw LFT input mask
#		Contains all SF, all NF and all WD as class (1) Perforating element
# rawInputMask=root+"Raw_LFT_Input_Mask"

# Threshold value for region group to separate buffers of NF and WD
# threshold=200

# Periods of LFT 
LFTs= ["2000","2005", "2010", "2015"]

# Build root folder structure to put final Master LFT input masks in
# Master folder
lftMaster = "Master"
for lft in LFTs:
	# Period folder
	outputFolder=str(lft)
	# Period folder path
	outputFolderPath = root+"/"+outputFolder
	# Create the folder if it doesn't exist
	if not os.path.exists(outputFolderPath):
		os.makedirs(outputFolderPath)
		print "Made "+str(lft)+" folder."
	# Create the master folder in it
	masterFolderPath=outputFolderPath+"/"+lftMaster
	if not os.path.exists(masterFolderPath):
		os.makedirs(masterFolderPath)
		print "Made Master folder for "+str(lft)+"."

# Insert path to raster to snap to 
tempEnvironment0 = arcpy.env.snapRaster
arcpy.env.snapRaster = r"C:\Data_Molinario\temp\LFT_local\19th_run\FACET_ROC\myfacet.tif"

# Set extent to FACET extent
arcpy.env.extent = r"C:\Data_Molinario\temp\LFT_local\19th_run\FACET_ROC\myfacet.tif"

arcpy.env.overwriteOutput=True


###############################################################################


################################################
# Manually build folders that are not automated: 
################################################

# - Raw_input_mask (unless I build it with script)
# - Core_stratification and Rural_complex folder (unless they are completely automated - check following. 
# 		- is the water distinction for core classification automated? 
# 		- is the focal distance creation for NF and WD automated? 
# - WaterAndNoData folder
# - AOI folder


################################################
# Readme - process to build LFT input mask
################################################

		# For 2000 include:
		#		Class 0: All water and NoData, all large NF and WD not close to loss. 
		#		Class 1: 
		#			- SF only if large groups or small groups if in proximity of PFL or SFL 2005/2010
		#				- Filtered for MMU, no single pixels
		#			- NF and WD only small groups if in proximity of PFL or SFL 2005/2010
		#				- Filtered for MMU, no single pixels go to NoData 
		#		Class 2: All PF

		# For 2005 include:
		#		Class 0: All water and NoData, all large NF and WD not close to loss. 
		#		Class 1: 
		#			As above, but also:
		#				- PFL, SFL and WDL 2005
		#		Class 2: All PF

		# For 2010 include:
		#		Class 0: All water and NoData, all large NF and WD not close to loss. 
		#		Class 1: 
		#			As above, but also:
		#				- PFL, SFL and WDL 2010
		#		Class 2: All PF

##########################################################
# Expand Primary,  secondary loss (and experimentally GFC)
##########################################################

# Develop code to do also "GFC" if wanted 
rasters=["PFL","SFL"]
# gfcYearlyLossFolder=r"Z:\Giuseppe\PhD\GFC\LossYear\Mosaic\ROC"
primaryLossFolder=facetMasks+"/" + "Primary_loss\Primary_loss_2000_2010"
secondaryLossFolder=facetMasks+"/"+"Secondary_loss\Secondary_loss_00_10"
outputFolder="Loss_expanded"
expandedMaskFolderPath=facetMaskWorkFolderPath+"/"+outputFolder
if not os.path.exists(expandedMaskFolderPath):
	os.makedirs(expandedMaskFolderPath)
	print "Made "+ outputFolder+" folder."

# Expand by how many pixels? 
numberCells=5

# area threshold in pixels for the minimum area buffer to keep (this corresponds to filtering out areas around about 1 loss px)
threshold=2000

# Make output folder
outputFolder="Within_loss_buffer"
# Period folder path
outputFolderPath = facetMaskWorkFolderPath+"/"+outputFolder
# Create the folder if it doesn't exist
if not os.path.exists(outputFolderPath):
 	os.makedirs(outputFolderPath)



# loop through and make expanded masks
for raster in rasters:
	if "PFL" in raster:
		env.workspace=primaryLossFolder	
		raster=arcpy.ListRasters()[0]
		print primaryLossFolder
	elif "SFL" in raster:
		env.workspace=secondaryLossFolder
		raster=arcpy.ListRasters()[0]
		# add and fix below if ou want to use GFC as well
	# elif "GFC" in raster:
	# 	env.workspace=gfcYearlyLossFolder
	# 	raster=arcpy.ListRasters("*total*")[0]
	else:
		pass
	print raster
	zoneValues=[1]
	outExpand = Expand(raster, numberCells, zoneValues)
	name="_exp_"+str(numberCells)+"px"
	rasterName=raster[:-4]+name+".tif"
	outExpand.save(expandedMaskFolderPath+"/"+rasterName)
	print "Saved output."

#################################################
# Merge together expanded pfl and sfl
#################################################

# versionsToMerge=["15","10"]
versionsToMerge=["5"]
print versionsToMerge
env.workspace=expandedMaskFolderPath
for version in versionsToMerge:
	pflMask=arcpy.ListRasters("*prim*"+version+"*")[0]
	sflMask=arcpy.ListRasters("secondary*"+version+"*")[0]
	mergedMask=Raster(pflMask)+Raster(sflMask)
	name="Merged_PFL_and_SFL_tot_exp_"+version+"px.tif"
	print name
	mergedMask.save(name)

###############################################
# Reclass merged output for focal stats
###############################################

rasters=arcpy.ListRasters("*Merged*")
print rasters
for raster in rasters:
	print raster
	reclassField = "Value"
	remap=RemapRange([
		[0,0,0],
		[1,2,1]])
	outReclassify=Reclassify(raster,reclassField,remap)
	# overwrite the previous merged rasters
	arcpy.env.overwriteOutput = True
	outReclassify.save(raster)

###############################################
# Focal stats to smooth the merged output
###############################################

rasters=arcpy.ListRasters("*Merged*px.tif*")
print rasters
for raster in rasters:
	print raster
 	neighbor=NbrCircle(12,"CELL")
 	outFS=FocalStatistics(raster,neighbor, "Mean", "")
	description="_crcl_12r"
 	outputRaster=raster[:-4]+description+".tif"
 	print outputRaster
 	outFS.save(outputRaster)

##############################################
# Reclass the focal stats output
##############################################

rasters=arcpy.ListRasters("*_crcl_12r*")
print rasters
for raster in rasters:
	print raster
	reclassField = "Value"
	remap=RemapRange([
 		[0,0.1,0],
		[0.1,1,1]])
	outReclassify=Reclassify(raster,reclassField,remap)
	description="_rcl"
	outputRaster=raster[:-4]+description+".tif"
 	outReclassify.save(outputRaster)



##############################################
# Region group and MMU
##############################################

env.workspace=expandedMaskFolderPath

# area threshold in pixels for the MMU is defined at top

# Loop through, region group and divide
rasters=arcpy.ListRasters("*_crcl_12r_rcl*")
for raster in rasters:
	print raster
	threshold=threshold # just a reminder, variable up at top
	# (set null to the looked up count values of the region group where a group is smaller then pixels of threshold)
	# Ignore value 1 (everything but the buffers) and region group value 0, 
	# then set to null if bigger then threshold, otherwise set to 1
	inTrueValue=0
	inFalseValue=1
	whereClause="VALUE >= "+str(threshold)
	lookupRaster=Lookup(RegionGroup(raster, "EIGHT", "WITHIN", "NO_LINK", "0"),"COUNT")
	rasterName=raster[:-8]+"_lkp.tif"
	arcpy.env.overwriteOutput = True
	lookupRaster.save(rasterName)
	RegionGrpRaster = Con(Raster(rasterName), inTrueValue, inFalseValue, whereClause)
	# Get the name of the raster
	rasterName = raster[:-8]
	print rasterName
	# Save the raster output
	# outputRaster= rasterName+"_RgnGrp_"+str(threshold)+"_NoD.tif"
	outputRaster= rasterName+"_RgnGrp_"+str(threshold)+".tif"
	arcpy.env.overwriteOutput = True
	RegionGrpRaster.save(outputRaster)

##############################################
# Subtract the small groups from mask
##############################################

rasters=arcpy.ListRasters("*_RgnGrp_*"+str(threshold)+"*.tif*")
for raster in rasters:
	if "10" in raster:
		print "input is " + raster
		rasterName=raster[:-4]+"lrg.tif"
		print "output is "+ rasterName
		onlyLargeBuffers=Raster(arcpy.ListRasters("*10*_crcl_12r_rcl*")[0])-Raster(raster)
		onlyLargeBuffers.save(rasterName)
	elif "15" in raster:
		print "input is " + raster
		rasterName=raster[:-4]+"lrg.tif"
		print "output is "+ rasterName
		onlyLargeBuffers=Raster(arcpy.ListRasters("*15*_crcl_12r_rcl*")[0])-Raster(raster)
		onlyLargeBuffers.save(rasterName)

	#Code below added later to build output name using the correct numberc ells being used
	else: 
		print "input is " + raster
		rasterName=raster[:-4]+"lrg.tif"
		print "output is "+ rasterName
		onlyLargeBuffers=Raster(arcpy.ListRasters("*"+str(numberCells)+"*_crcl_12r_rcl*")[0])-Raster(raster)
		onlyLargeBuffers.save(rasterName)




##################################################
# Now use this mask to select secondary forest
##################################################



env.workspace=expandedMaskFolderPath
# the version you want to use (just var numberCells if only one version was created)
selectedPxExpansion=numberCells


# the final loss mask to load up in memory
lossMask=arcpy.ListRasters("*"+str(selectedPxExpansion)+"*_RgnGrp_*"+str(threshold)+"*lrg.tif*")[0]
# get full path
lossMaskPath=env.workspace+"/"+lossMask
env.workspace=sfMaskFolder
sfInput=arcpy.ListRasters("*SF_only_not_inc_loss_2000.tif*")[0]
# add sf mask and loss mask 
selectSF=Raster(lossMaskPath)+Raster(sfInput)
outputName="SF_2000_In_Loss_Buff.tif"
# save it to new folder
env.workspace=outputFolderPath
selectSF.save(outputName)


##############################################
# Reclass selected SF within this buffer area
##############################################

selectSF=arcpy.ListRasters("*SF_2000_In_Loss_Buff.tif*")[0]
reclassField = "Value"
rename=selectSF[:-4]+"_rcl.tif"
remap=RemapValue([
 	[0,0],
 	[1,0],
 	[2,1]])
outReclassify=Reclassify(selectSF,reclassField,remap)
# overwrite the previous merged rasters
# arcpy.env.overwriteOutput = True
outReclassify.save(rename)


##############################################
# Expand selected secondary forest
##############################################

selectSF=arcpy.ListRasters("*SF_2000_In_Loss_Buff_rcl.tif*")[0]
numberCells=selectedPxExpansion # from above - the px expansion selected to be used (10 or 15 or)
zoneValues=[1]
outExpand = Expand(selectSF, numberCells, zoneValues)
name="_exp_"+str(numberCells)+"px"
rasterName=selectSF[:-8]+name+".tif"
outExpand.save(outputFolderPath+"/"+rasterName)
print "Saved expdanded SF"


###############################################
# Focal stats to smooth the expanded SF
###############################################

env.workspace=outputFolderPath
raster=arcpy.ListRasters("*px.tif*")[0]
print rasters

print raster
neighbor=NbrCircle(12,"CELL")
outFS=FocalStatistics(raster,neighbor, "Mean", "")
description="_crcl_12r"
outputRaster=raster[:-4]+description+".tif"
print outputRaster
outFS.save(outputRaster)

##############################################
# Reclass focal stats output
##############################################

raster=arcpy.ListRasters("*_crcl_12r*")[0]
print raster
reclassField = "Value"
remap=RemapRange([
	# previous 
	# [0,0.1,0],
	# [0.1,1,1]])
 	[0,0.624,0],
	[0.624,1,1]])
outReclassify=Reclassify(raster,reclassField,remap)
description="_rcl"
outputRaster=raster[:-4]+description+".tif"
outReclassify.save(outputRaster)

##############################################
# Region group and MMU
##############################################

# area threshold in pixels for the minimum area buffer to keep
threshold=2000
raster=arcpy.ListRasters("*_crcl_12r_rcl*")[0]
print raster
threshold=threshold # just a reminder, variable up at top
	# (set null to the looked up count values of the region group where a group is smaller then pixels of threshold)
	# Ignore value 1 (everything but the buffers) and region group value 0, 
	# then set to null if bigger then threshold, otherwise set to 1
inTrueValue=0
inFalseValue=1
whereClause="VALUE >= "+str(threshold)
lookupRaster=Lookup(RegionGroup(raster, "EIGHT", "WITHIN", "NO_LINK", "0"),"COUNT")
rasterName=raster[:-8]+"_lkp.tif"
#arcpy.env.overwriteOutput = True
lookupRaster.save(rasterName)
RegionGrpRaster = Con(Raster(rasterName), inTrueValue, inFalseValue, whereClause)
# Get the name of the raster
rasterName = raster[:-8]
print rasterName
# Save the raster output
# outputRaster= rasterName+"_RgnGrp_"+str(threshold)+"_NoD.tif"
outputRaster= rasterName+"_RgnGrp_"+str(threshold)+".tif"
# arcpy.env.overwriteOutput = True
RegionGrpRaster.save(outputRaster)

##############################################
# Subtract small groups from mask
##############################################

raster=arcpy.ListRasters("*_RgnGrp_*"+str(threshold)+"*.tif*")[0]
print "input is " + raster
rasterName=raster[:-4]+"lrg.tif"
print "output is "+ rasterName
onlyLargeBuffers=Raster(arcpy.ListRasters("*"+str(numberCells)+"*_crcl_12r_rcl*")[0])-Raster(raster)
onlyLargeBuffers.save(rasterName)



##############################################
# Add buffered SF to Loss buffer
##############################################

env.workspace=expandedMaskFolderPath
lossBuffer=arcpy.ListRasters("*"+str(numberCells)+"*lrg.tif")[0]
lossBufferPath=env.workspace+"/"+lossBuffer
env.workspace=outputFolderPath
sfBuffer=arcpy.ListRasters("*lrg.tif*")[0]
mergedMask=Raster(lossBufferPath)+Raster(sfBuffer)
name=sfBuffer[:-4]+"_mrg.tif"
mergedMask.save(name)


##############################################
# reclass to 100 to keep things sorted when added to FACET
##############################################
env.workspace=outputFolderPath
raster=arcpy.ListRasters("*lrg_mrg.tif*")[0]
print raster
reclassField = "Value"
remap=RemapValue([
 	[0,0],
	[1,100],
	[2,100]])
outReclassify=Reclassify(raster,reclassField,remap)
description="_rcl"
outputRaster=raster[:-4]+description+".tif"
outReclassify.save(outputRaster)

##############################################
# # Now add this area to facet
##############################################

env.workspace=facetFolder
facet=arcpy.ListRasters()[0]
print facet
facetPath=facetFolder+"/"+facet
env.workspace=outputFolderPath
raster=arcpy.ListRasters("*lrg_mrg_rcl.tif*")[0]
addFacet=Raster(facetPath)+Raster(raster)
name="Facet_merged_w_SF_and_Loss_buffer.tif"
print name
addFacet.save(name)




####################################################################
# Reclass product into mask for LFT
#
# 	Version A. 
# 	
#	In this version: 
#		Outside the buffer of loss:
#			WD is classified as 0
#			WDL is classified as 1 (Fragmenting land cover) as RURAL COMPLEX. 
#		Inside the buffer:
#			WD is classified as 1
#			WDL is classified as 1 in 2000, 2005, 2010 (like secondary forest)
#
# 	This is the version used.
#
####################################################################



#maskVersion="v14_r4_1"
maskVersion="19"

wdLossVariant=outputFolderPath+"\Version_w_WDL_outs_buff_as_fragmenting_class"
# Create the folder if it doesn't exist
if not os.path.exists(wdLossVariant):
 	os.makedirs(wdLossVariant)

env.workspace=outputFolderPath
# create this raster 	
raster=arcpy.ListRasters("*Facet_merged_w_SF_and_Loss_buffer.tif*")[0]
print raster
#periods=["2000","2005","2010","2015"]
periods=["2000"]
reclassField = "Value"

# LFT input classes
# Class 0 = not included in analysis\
# Class 1 = fragmenting land cover (clearing)
# Class 2 = fragmented land cover (forest)

for period in periods: 
	env.workspace=outputFolderPath
	if "2000" in period:
		remap=RemapRange([
		# Outside of buffer
	 	[0,4,0], # No data, water, NF and WD 
		[5,5,2], # primary forest
		[6,6,0], # SF
		[7,7,0], # WDL 2005
		[8,8,2], # PFL 2005
		[9,9,0], # SFL 2005 
		[10,10,0], # WDL 2010
		[11,11,2], # PFL 2010 
		[12,12,0], # SFL 2010
		# Inside of buffer
		[100,100,0], # No data
		[101,101,1], # NF in buffer
		[102,102,0], # Water
		[103,103,0], # No data 
		[104,104,1], # WD in buffer
		[105,105,2], # PF
		[106,106,1], # SF 
		[107,107,0], # WDL 2005 in buffer (has to start as either 0/2 to become 1)
		[108,108,2], # PFL 2005
		[109,109,1], # SFL 2005 
		[110,110,0], # WDL 2010 in buffer (has to start as either 0/2 to become 1)
		[111,111,2], # PFL 2010
		[112,112,1]]) # SFL 2010 in buffer
		name="ROC_"+period+"_Mask_for_LFT_v"+maskVersion+".tif"

	elif "2005" in period:
		remap=RemapRange([
		# Outside of buffer
	 	[0,4,0], # No data, water, NF and WD 
		[5,5,2], # primary forest
		[6,6,0], # Secondary forest
		# Difference below with v B.
		[7,7,1], # WDL 2005 (0 in v B.)
		[8,8,1], # PFL 2005
		[9,9,1], # SFL 2005
		[10,10,0], # WDL 2010
		[11,11,2], # PFL 2010 
		[12,12,0], # SFL 2010
		# Inside buffer
		[100,100,0], # No data
		[101,101,1], # NF in buffer
		[102,102,0], # Water
		[103,103,0], # No data 
		[104,104,1], # WD in buffer
		[105,105,2], # PF
		[106,106,1], # SF
		[107,107,1], # WDL 2005 in buffer (was 0)
		[108,108,1], # PFL 2005 (was 2)
		[109,109,1], # SFL 2005 (always 1)
		[110,110,0], # WDL 2010 in buffer
		[111,111,2], # PFL 2010
		[112,112,1]]) # SFL 2010 in buffer
		name="ROC_"+period+"_Mask_for_LFT_v"+maskVersion+".tif"

	elif "2010" in period:
		remap=RemapRange([
		# Outside Buffer
	 	[0,4,0], # No data, water, NF and WD 
		[5,5,2], # Primary forest
		[6,6,0], # SF
		[7,7,1], # WDL 2005 (0 in v B.)
		[8,8,1], # PFL 2005
		[9,9,1], # SFL 2005
		[10,10,1], # WDL 2010
		[11,11,1], # PFL 2010
		[12,12,1], # SFL 2010
		# Inside buffer
		[100,100,0], # No data
		[101,101,1], # NF in buffer
		[102,102,0], # Water
		[103,103,0], # No data 
		[104,104,1], # WD in buffer
		[105,105,2], # PF
		[106,106,1], # SF
		[107,107,1], # WDL 2005 in buffer
		[108,108,1], #	PFL 2005
		[109,109,1], # SFL 2005
		[110,110,1], # WDL 2010 in buffer (was 0)
		[111,111,1], # PFL 2010 (was 2) 
		[112,112,1]]) # sfl 2010 in buffer (always 1)
		name="ROC_"+period+"_Mask_for_LFT_v"+maskVersion+".tif"
	
	else:
		pass

	outReclassify=Reclassify(raster,reclassField,remap)
	env.workspace=wdLossVariant
	print env.workspace
	print name
	outReclassify.save(name)
	print "Mask for "+ period + " exported. Version "+maskVersion



##################################################################
# Reclass product into mask selecting only SF, NF and WD within it 
# 
# 	Version B. 
#
#	In this version:
#		Outside the buffer:
#			WD is classified as 0
#			WDL is classified as 0
#		Inside the buffer:
#			WD is classified as 1
#			WDL is classified 1 in 2000,2005,2010 like SF loss
# 
#
###################################################################

# Comment out 
'''
maskVersion="v15"

env.workspace=outputFolderPath
raster=arcpy.ListRasters("*Facet_merged_w_SF_and_Loss_buffer.tif*")[0]
print raster
periods=["2000", "2005", "2010","2014"]

# mask version to be created and copied to lft folder
reclassField = "Value"
# below for 2000
#
for period in periods: 
	if "2000" in period:
		remap=RemapRange([
		# Outside of buffer
	 	[0,4,0], # No data, water, NF and WD 
		[5,5,2], # primary forest
		[6,6,0], # SF
		[7,7,0], # WDL 2005 
		[8,8,2], # PFL 2005
		[9,9,0], # SFL 2005 
		[10,10,0], # WDL 2010
		[11,11,2], # PFL 2010 
		[12,12,0], # SFL 2010
		# Inside buffer
		[100,100,0], # no data
		[101,101,1], # NF in buffer
		[102,102,0], # Water
		[103,103,0], # No data 
		[104,104,1], # WD in buffer
		[105,105,2], # PF
		[106,106,1], # SF 
		[107,107,1], # WDL 2005 in buffer
		[108,108,2], # PFL 2005
		[109,109,1], # SFL 2005
		[110,110,1], # WDL 2010 in buffer
		[111,111,2], # PFL 2010
		[112,112,1]]) # SFL 2010 in buffer
		name="ROC_"+period+"_Mask_for_LFT_v"+maskVersion+".tif"

	elif "2005" in period:
		remap=RemapRange([
		# Outside buffer
	 	[0,4,0], # No data, water, NF and WD 
		[5,5,2], # Primary forest
		[6,6,0], # SF
		# Difference below
		[7,7,0], # WDL 2005
		[8,8,1], # PFL 2005 
		[9,9,1], # SFL 2005 
		[10,10,0], # WDL 2010
		[11,11,2], # PFL 2010 
		[12,12,0], # SFL 2010
		# Inside buffer
		[100,100,0], # No data
		[101,101,1], # Non forest in buffer
		[102,102,0], # water
		[103,103,0], # No data 
		[104,104,1], # WD in buffer
		[105,105,2], # PF
		[106,106,1], # SF
		[107,107,1], # WDL 2005 in buffer
		[108,108,1], # PFL 2005
		[109,109,1], # SFL 2005 
		[110,110,1], # WDL 2010 in buffer
		[111,111,2], # PFL 2010
		[112,112,1]]) # SFL 2010 in buffer 
		name="ROC_"+period+"_Mask_for_LFT_v"+maskVersion+".tif"

	elif "2010" in period:
		remap=RemapRange([
		# Outside buffer
	 	[0,4,0], # No data, water, NF and WD 
		[5,5,2], # primary forest
		[6,6,0], # Secondary forest 
		# difference below
		[7,7,0], # WDL 2005
		[8,8,1], # PFL 2005  
		[9,9,1], # SFL 2005 
		[10,10,0], # WDL 2010
		[11,11,1], # PFL 2010
		[12,12,1], # SFL 2010 
		# Inside buffer
		[100,100,0], # no data
		[101,101,1], # Non forest in buffer
		[102,102,0], # water
		[103,103,0], # No data 
		[104,104,1], # WD in buffer
		[105,105,2], # PF
		[106,106,1], # SF
		[107,107,1], # WDL 2005 in buffer
		[108,108,1], # PFL 2005
		[109,109,1], # SFL 2005 
		[110,110,1], # WDL 2010 in buffer
		[111,111,1], # PFL 2010
		[112,112,1]]) # SFL 2010 in buffer 
		name="ROC_"+period+"_Mask_for_LFT_v"+maskVersion+".tif"

	else:
		pass

	outReclassify=Reclassify(raster,reclassField,remap)
	arcpy.env.overwriteOutput = True
	outReclassify.save(name)


'''

##########################################################
# Copy the final LFT masks into the master folders
##########################################################
lftVersion="19"
maskVersion="v19"

env.workspace=wdLossVariant
rasters=arcpy.ListRasters("*LFT_*"+maskVersion+"*.tif*")
print rasters
for raster in rasters:
	if "2000" in raster:
		dst=root+"/2000/Master/"+raster
		arcpy.CopyRaster_management(raster,dst,"DEFAULTS","","","","","")
	elif "2005" in raster:
		dst=root+"/2005/Master/"+raster
		arcpy.CopyRaster_management(raster,dst,"DEFAULTS","","","","","")
	else:
		dst=root+"/2010/Master/"+raster
		arcpy.CopyRaster_management(raster,dst,"DEFAULTS","","","","","")


# put those masks in the LFT folder. 

# 4/2018 - for ROC version there are a couple error values (-1 &-2 for about 600 pixels in total)
# run the clean master for LFT script
# Then run the build hybrid mask script 






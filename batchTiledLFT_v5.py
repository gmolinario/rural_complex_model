# Script name: batchTiledLFT_v4.py

# Authors: Giuseppe Molinario and Mike Humber (UMD)
# LFT code (separate script) by Jason Parent (UConn)
# Date of last update: 
# 03/2014
# 07/25/2016
# 04/30/2018

# What the script does: 
# 		- It tiles a large input mask image for LFT (see LFT requirements), 
# 		- runs the LFT on all the tiles, 
# 		- clips the output LFT tiles in order to remove edge effects,
# 		- finally mosaics the LFT output tiles back together into a single image. 
# 		- The script also makes a copy of the LFT temporary analysis folder,
#	 		renaming it with the name of the tile. This setting can be disabled. 
#
# The location of the TempWS folder should be changed also in the LFT_SA_GM.py script 
# 	to match the location set in the variables of this script. 


# Import
import arcpy
import os
from arcpy.sa import *
import shutil

#####################################################################
# User defined variables:
#####################################################################

# List of analysis years
#### - Copy year 2000 folder into v1x cause it hasnt changed since v14 (unless ROC - v19)
# years=[2000,2005,2010]
years=[2005,2010,2015]


# Region of interest name? 
roi="ROC"

# Location of the LFT script 
lftScript = ("C:\\Data_Molinario\\Dropbox\\PhD\\Scripts\\LFT\\LFT_SA_gm_test_more_core_clss.py")

# Set to 1 if you want a copy of the LFT temporary data folder made for each LFT tile
copyTemp = 0

# Distance in meters for the LFT edge/buffer
lftEdge = "240"

# Input image pixel size (find pixel size in image properties)
pixelSize = 60

# Tile size in pixels assuming it's a square. The tile size depends on your preference. 
# tileSize = 6200 # (DRC)
tileSize=5197 # (ROC)

# Overlap of the tiles in pixels
# 		This is necessary so that the LFT will not have edge effects.
#		The input image extent should be divisible by tilesize-overlap
# 		i.e. image extent/(tilesize - overlap) = no remainder
# 		The overlap size depends on your preference, but 200px works well. 
# overlap = 200 # (DRC)
overlap=0

# Set extent and snap to FACET (DRC/ROC) extent
arcpy.env.extent = r"C:\Data_Molinario\Temp\LFT_local\19th_run\FACET_ROC\myfacet.TIF"
arcpy.env.snapRaster = r"C:\Data_Molinario\Temp\LFT_local\19th_run\FACET_ROC\myfacet.TIF"

#########################################################################
# Giant for loop to cycle all the code below to all analysis years wanted 
#########################################################################
for year in years:

	# Set base directory 
	root="C:/Data_Molinario/temp/LFT_local/19th_run/"

	# Set arcpy workspace for loading master NF/F mask
	arcpy.env.workspace = root+str(year)+"/Master/"
	masterList=arcpy.ListRasters()
	for master in masterList:
		# Input tif file (forest/non-forest mask for LFT)
		print master
		inputFile=arcpy.env.workspace+"/"+master
		print inputFile

	# Set arcpy workspace for tiling
	# Reset this for each folder (2000,2005,2010)
	arcpy.env.workspace = root+str(year)+"/"
	workspace= arcpy.env.workspace

	# Location of the LFT temp folder, needed because for every tile the contents are moved and renamed to the tiles folder
	lftTempFolder = root+"/TempWS"


	#####################################################################
	# Creation of folder structure
	#####################################################################
	
	# Name of tiles folders to be created
	tileFolderName = "1_Input_Tiles"
	tileFolderPath = workspace+"/"+tileFolderName
	# Create the folder if it doesn't exist
	if not os.path.exists(tileFolderPath):
		os.makedirs(tileFolderPath)

	# Name of LFT tiles output folder
	outFolderLFTTiles = "2_Output_LFT_Tiles"
	lftTilesPath = workspace+"/"+outFolderLFTTiles 
	# Create the folder if it doesn't exist
	if not os.path.exists(lftTilesPath):
		os.makedirs(lftTilesPath)

	# Create the folder for the clipped LFT tiles
	clippedFolderName= "3_Clipped_LFT_Tiles"
	clippedFolder = workspace+"/"+clippedFolderName
	# Create the folder if it doesn't exist
	if not os.path.exists(clippedFolder):
		os.makedirs(clippedFolder)

	# Name of the final mosaic folder
	mosaicFolderName = "4_Output_LFT_Mosaic"
	mosaicFolderPath = workspace+"/"+mosaicFolderName
	# Create the folder if it doesn't exist
	if not os.path.exists(mosaicFolderPath):
		os.makedirs(mosaicFolderPath)

	# Concatenate name of output LFT image mosaic 
	mosaicFileName = roi+"_"+str(year)+"_"+lftEdge+"_"+"Mosaic.tif"


	
	##################################################################
	# Tiling input image
	##################################################################

	# Find the raster's Xmin and Ymin in order to determine origin for tiling
	imageOpened = Raster(inputFile)
	XMin = imageOpened.extent.XMin
	YMin = imageOpened.extent.YMin

	# Create the string that contains the origin (offset) from which to start the tiling 
	origin= str(XMin-((overlap/2)*pixelSize))+" "+str(YMin-((overlap/2)*pixelSize))

	# Create the string that contains the tile size
	tileSizeString=str(tileSize)+" "+str(tileSize)

	print "Tiling input..."
	print "origin: "+ origin + " " + "tile size: "+ tileSizeString

	# Tile the image using the tile size and overlap parameters. 
	arcpy.SplitRaster_management(inputFile, tileFolderPath, inputFile.replace('.tif', "_"+str(tileSize)+"_x_"+str(tileSize)+"_tile_"), "SIZE_OF_TILE",\
	                             "TIFF", "BILINEAR","#", tileSizeString, overlap, "PIXELS",\
	                             "#", origin)


	print "The tiles have now been created in: "+tileFolderPath


	#######################################################################
	# Run the LFT on all tiles
	#######################################################################

	# Reset arcpy workspace in order to use arcpy.ListRasters again
	arcpy.env.workspace = (tileFolderPath)

	# List Rasters in tile folder
	theInputTiles = arcpy.ListRasters()

	# Iterate the LFT on all the tiles in the folder
	for inputTile in theInputTiles:
	    inFile = os.path.join(tileFolderPath,inputTile)
	    outraster = inputTile[:-4]
	    #outraster = os.path.splitext(inputTile)
	    outFile = lftEdge+"_"+"LFT"+"_"+outraster
	    print "python "+lftScript+" "+inFile+" "+lftEdge+" "+lftTilesPath+" "+outFile
	    handle = os.system("python "+lftScript+" "+inFile+" "+lftEdge+" "+lftTilesPath+" "+outFile)
	    print inFile
	    print lftTilesPath
	    print outFile
	    if copyTemp == 1:
	    	shutil.move(lftTempFolder, lftTilesPath+"/"+inputTile.replace(".TIF","_LFT_Temp"))
	    else:
	    	print "The Temp folder is not being saved."
	    	pass
	print "LFT has been run on all the tiles. " 

	
	######################################################################
	# Clipping all the output LFT tiles to remove edge effects
	######################################################################

	# Set the new workspace
	arcpy.env.workspace = (lftTilesPath)

	# Make a list of all the LFT tiles
	rasters = arcpy.ListRasters()

	# Convert the pixel overlap to meters:
	overlapMeters = (overlap/2)*pixelSize

	# Iterate through the tiles to trim edges
	for image in rasters:
		imageOpened = Raster(image)
		XMin = imageOpened.extent.XMin
		YMin = imageOpened.extent.YMin
		XMax = imageOpened.extent.XMax
		YMax = imageOpened.extent.YMax
		print "LFT tile name: "+ image

		# Make a string with xmin ymin xmax ymax to be passed to clip tool
		envelope=str(XMin+overlapMeters)+" "+ str(YMin+overlapMeters)+" "+str(XMax-overlapMeters)+" "+str(YMax-overlapMeters)
		print envelope

		# Make a new name for each output raster
		clippedTile = image.replace('.TIF',"_clip2.tif")
		print "Clipped tile name: "+ clippedTile

		# Clip each LFT tile
		arcpy.Clip_management(image, envelope, clippedFolder+"/"+clippedTile, "#", "#", "NONE")

	print "All the LFT tiles have been clipped. "

	

	######################################################################
	# Mosaic the LFT tiles back into a single image
	######################################################################

	# Set new workspace to LFT tile path 
	arcpy.env.workspace = clippedFolder

	# Make a list of all the LFT tiles
	rasters = arcpy.ListRasters()
	print rasters
	print mosaicFolderPath
	print mosaicFileName
	# Set extent to FACET extent
	arcpy.env.extent = r"C:\Data_Molinario\Temp\LFT_local\19th_run\FACET_ROC\myfacet.TIF"
	# Mosaic the individual clipped LFT tiled TIFF images to a mosaic TIFF 
	arcpy.MosaicToNewRaster_management(rasters, mosaicFolderPath, mosaicFileName, "#", "#", "#", "1", "#","#")

	# 06/09/2014
	# Creates a final 8 class mosaic with:
	# 0 non forest
	# 1 patch forest
	# 2 edge forest
	# 3 perforated forest
	# 4 small frag for
	# 5 med frag for 
	# 6 large frag for
	# 7 core for


	print "The final LFT mosaic has been created."

	# End
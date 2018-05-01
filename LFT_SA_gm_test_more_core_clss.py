# Author: Jason Parent
# Date: 5-Jan-09
# PURPOSE: This script analyzes the type of fragmentation present in the specified
# land cover types (i.e. forest).

# The analysis in this script is equivalent to the procedure developed by Vogt et al. (2007) -
# testing has confirmed that this script generates identical results. The procedure used by
# Vogt et al. (2007) can be found in the following paper:

#   Vogt, P., K. Riitters, C. Estrenguil, J. Kozak, T. Wade, J. Wickham. 2007. Mapping spatial patterns
#       with morphological image processing. Landscape Ecology 22: 171-177

#-------------------------------------------------
########## 
#### Giuseppe Molinario changes:  
#### - changed the path to FragData temp directory as the native root of C: made it crash.
#### - allowed for tempMW temp directory to be left (original script deletes it)
#### - made the temp file nf_c_p_grps.img be written with the tile name and sent to 
########## 

#-------------------------------------------------
# SCRIPT REQUIREMENTS...

# THIS SCRIPT DOES NOT REQUIRE THE SPATIAL ANALYST EXTENSION.
# IT WILL WORK WITH THE ARCVIEW LEVEL OF ARCGIS 9.3
# SCRIPT WAS DESIGNED USING PYTHON 2.5 - IT MAY NOT WORK WITH EARLIER VERSIONS.

#-------------------------------------------------
# ACKNOWLEDEMENTS...

# The analysis in this script is equivalent to the procedure developed by Vogt et al. (2007) -
# testing has confirmed that this script generates identical results. The procedure used by
# Vogt et al. (2007) can be found in the following paper:

#   Vogt, P., K. Riitters, C. Estrenguil, J. Kozak, T. Wade, J. Wickham. 2007. Mapping spatial patterns
#       with morphological image processing. Landscape Ecology 22: 171-177

#-------------------------------------------------

# Note: the analysis has been modified from Vogt et al. (2007) to sub-classify core patches
# into three categories based on area.

#-------------------------------------------------
# DESCRIPTION OF OUTPUT...

# The script will generate a raster that contains the following values:
#   0: the fragmenting class (i.e. non-forest)
#   1: patch
#   2: edge
#   3: perforated  
#   4: core < X ha (see line 332) 
#   5: core >= X ha < Y ha (see line 328)
#   6: core >= Y ha (see line 325)

# core thresholds decided by GM

# Core thresholds based on research done on minimum viable forest patch sizes.
# See http://sof.eomf.on.ca/Biological_Diversity/Ecosystem/Fragmentation/Indicators/Size/i_wooded_patch_size_by_watershed_e.htm
# for more information.

#---------------------------------------------------

# import required modules...
import sys, os, arcgisscripting, time, traceback
print sys.argv
try:

    # create the geoprocessor
    gp = arcgisscripting.create(10.3)
    
    # enable the overwrite option...
    gp.OverwriteOutput = 1
    
    # check out spatial analyst license...
    gp.CheckOutExtension("spatial")
    
    # load spatial analyst toolbox...
##    gp.AddToolbox(r"C:\Program Files\ArcGIS\ArcToolbox\Toolboxes\Spatial Analyst Tools.tbx")
##    gp.AddToolbox(r"C:\Program Files\ArcGIS\ArcToolbox\Toolboxes\Data Management Tools.tbx")
  
    #script parameters...
    landcover = sys.argv[1]         # input raster dataset
    edgeWidth = sys.argv[2]         # string
    wksp = sys.argv[3]              # output raster location
    FragMap_lyr = sys.argv[4]       # display layer

    
    s = time.clock()
    
    #-----------------------------------------------------------
    # CREATE OUTPUT RASTER NAME FROM WORKSPACE AND LAYER NAME...
            
    # if workspace is a geodatabase, no extension needed...
    if ".gdb" in wksp or ".mdb" in wksp:
        FragMap = "%s\\%s" % (wksp,FragMap_lyr)
    
    # otherwise use ".img" extension (no length / character restrictions)...
    else:    
        FragMap = "%s\\%s.img" % (wksp,FragMap_lyr)
    
    # provide user feedback...
    gp.AddMessage("\nOUTPUT DATASET NAME IS:")
    print "\nOUTPUT DATASET NAME IS:"
    gp.AddMessage("\n\t%s\n" % FragMap)
    print "\n\t%s\n" % FragMap
    
    
    
    #-----------------------------------------------------------
    # DETERMINE PROJECTION UNITS...
    
    desc = gp.describe(landcover)    # describe object
    cellsize = desc.MeanCellHeight   # cell size
    spatRef = desc.SpatialReference
    units = spatRef.LinearUnitName    # projection units
    
    # Note: output units are the same as the input units
    
    # Note: area thresholds based on hectares (will need to convert units to meters)
    
    if "Foot" in units:
        cf = .3048      # correction factor to convert feet to meters
    elif "Meter" in units:
        cf = 1          # no correction needed
    
    # if units are not in feet or meters, full analysis cannot be completed - exit script...
    else:
        print "Land cover has unknown units. Data may be unprojected or projection may be undefined."
        gp.AddError("Land cover has unknown units. Data may be unprojected or projection may be undefined.")
        sys.exit(1)     # exit script with failure
    
    del desc
    
    #-----------------------------------------------------------
    # VALIDATE EDGE WIDTH PARAMETER...
    
    # edge width parameter must be greater than or equal to cellsize...
    if edgeWidth < cellsize:
        print "\nEDGE WIDTH MUST BE GREATER THAN OR EQUAL TO PIXEL WIDTH\n"
        gp.AddError("\nEDGE WIDTH MUST BE GREATER THAN OR EQUAL TO PIXEL WIDTH\n")
        sys.exit(1)     # exit script with failure
    
    #-----------------------------------------------------------
    # SET UP TEMPORARY FOLDER FOR TEMPORARY DATA...
    
    # temporary workspace location...
    #TempWS = "C:\\Temp_damn_LFT"
    TempWS = r"C:\Data_Molinario\temp\LFT_local\16th_run\TempWS"
    # check if temp workspace exists...
    if not gp.exists(TempWS):
        # create folder if it doesn't exist...
        os.makedirs(TempWS) 
    
    #---------------------------------------------------
    # EXTRACT DATA FROM LAND COVER RASTER...
    
    # extract fragmented class from land cover...
    f1_ras = TempWS + "\\f1_.img"
    gp.Reclassify_sa (landcover, "Value", "2 1", f1_ras, "NODATA")
    
    # extract fragmenting class from land cover...
    nf1_ras = TempWS + "\\nf1_.img"
    gp.Reclassify_sa (landcover, "Value", "1 1", nf1_ras, "NODATA")
    
    gp.AddMessage("DATA EXTRACTED FROM LAND COVER")
    print "DATA EXTRACTED FROM LAND COVER"
    #---------------------------------------------------
    # EXTRACT EDGE CLASS FOR FRAGMENTED LAND COVER...
    
    # buffer fragmented class by width of edge zone...
    f_buf = TempWS + "\\f_buf.img"
    gp.EucDistance_sa(f1_ras, f_buf, edgeWidth, cellsize)
    
    # extract fragmenting class periphery (1) and core (2)...
    nf_peri_core = TempWS + "\\nf_p_c.img"
    remap = "0 NoData;0 %s 1;NoData 2" % edgeWidth      
    gp.Reclassify_sa (f_buf, "Value", remap, nf_peri_core)
    
    # region group fragmenting class...
    nf_grp = TempWS + "\\nf_grp.img"
    gp.RegionGroup_sa(nf1_ras, nf_grp, "EIGHT", "WITHIN")  
    
    # identify fragmenting class groups as core or periphery...
    nf_core_peri_grps = TempWS + "\\nf_c_p_grps.img"
    gp.ZonalStatistics_sa(nf_grp, "VALUE", nf_peri_core, nf_core_peri_grps, "MAXIMUM", "DATA")
    
    # extract fragmenting class core groups...
    nf_core = TempWS + "\\nf_core.img"
    gp.Reclassify_sa (nf_core_peri_grps, "Value", "2 1", nf_core, "NODATA")
    
    # buffer fragmenting class core groups by width of edge zone...
    nf_core_buf = TempWS + "\\nf_core_buf.img"
    gp.EucDistance_sa(nf_core, nf_core_buf, edgeWidth, cellsize)
    
    # extract edge forest (1)...
    edge = TempWS + "\\edge.img"
    remap = "0 NoData;0 %s 1;NoData 0" % edgeWidth
    gp.Reclassify_sa (nf_core_buf, "Value", remap, edge)
    
    gp.AddMessage("EDGE FRAGMENTATION IDENTIFIED")
    print "EDGE FRAGMENTATION IDENTIFIED"
    
    #---------------------------------------------------
    # EXTRACT PATCH, CORE, AND PERIPHERY OF FRAGMENTED CLASS...
    
    # buffer fragmenting class by width of edge zone...
    nf_buf = TempWS + "\\nf_buf.img"
    gp.EucDistance_sa(nf1_ras, nf_buf, edgeWidth, cellsize)
    
    # extract core and periphery of fragmented class...
    f_peri_core = TempWS + "\\f_p_c.img"
    remap = "0 NoData;0 %s 2;NoData 4" % edgeWidth
    gp.Reclassify_sa (nf_buf, "Value", remap, f_peri_core, "NODATA")  
    
    # region group fragmented class...
    f_grp = TempWS + "\\f_grp.img"
    gp.RegionGroup_sa(f1_ras, f_grp, "FOUR", "WITHIN")
    
    # identify fragmented class groups as core or periphery...
    f_core_peri_grps = TempWS + "\\f_c_p_grps.img"
    gp.ZonalStatistics_sa(f_grp, "VALUE", f_peri_core, f_core_peri_grps, "MAXIMUM", "DATA")
    
    # extract patch forest (0)...
    patch0_1 = TempWS + "\\patch0_1.img"
    remap = "2 0;4 1;NoData 1"
    gp.Reclassify_sa (f_core_peri_grps, "Value", remap, patch0_1, "NODATA") 
    
    gp.AddMessage("INTERIOR, PATCH, AND PERFORATED FRAGMENTATION IDENTIFIED")
    print "INTERIOR, PATCH, AND PERFORATED FRAGMENTATION IDENTIFIED"
    #---------------------------------------------------
    # COMBINE FRAGMENTATION CLASSES AND CREATE FINAL FRAGMENTATION MAP...
    
    # combine fragmented class edge, core, and perforated...
    nonPatch = TempWS + "\\nonPatch.img"
    gp.Plus_sa(f_peri_core, edge, nonPatch)
    
    # combine non-patch classes with patch - for fragemented class...
    fragMap1 = TempWS + "\\fragMap1.img"
    gp.Times_sa(nonPatch, patch0_1, fragMap1)
    
    # reclassify patch forest to 1...
    fragMap2 = TempWS + "\\fragMap2.img"
    gp.Reclassify_sa (fragMap1, "Value", "0 1", fragMap2, "DATA") 
    
    # clip fragMap to fragmented class pixels only...
    fragMap2_f = TempWS + "\\fragMap2_f.img"
    gp.Times_sa(fragMap2, f1_ras, fragMap2_f)
    
    #-------------------------------------------------------------------
    
    # DETERMINE PROJECTION UNITS...
    
    desc = gp.describe(landcover)    # describe object
    cellsize = desc.MeanCellHeight   # cell size
    spatRef = desc.SpatialReference
    units = spatRef.LinearUnitName    # projection units
    
    # Note: output units are the same as the input units
    
    # Note: area thresholds based on hectares (will need to convert units to meters)
    # before the conversion was from meters to feet - modified by GM
    
    if "Foot" in units:
        cf = 0.3048           # no correction needed
         
    elif "Meter" in units:
        cf = 1          # correction factor to convert meters to feet
    
    # if units are not in feet or meters, full analysis cannot be completed - exit script...
    else:
        print "Land cover is not in meters or feet. Data may be unprojected or projection may be undefined."
        gp.AddError("Land cover has unknown units. Data may be unprojected or projection may be undefined.")
        sys.exit(1)     # exit script with failure
    
    del desc
    
    
    
    # CLASSIFY CORE FOREST BASED ON PATCH SIZE
    
    
    gp.workspace = TempWS
    
    gp.AddMessage("CATEGORIZING CORE FOREST PATCHES...")
    print "CATEGORIZING CORE FOREST PATCHES..."
    
    gp.Reclassify_sa (fragMap2_f, "Value", "4 1", "core1_", "NODATA")
    
    # region group core class...
    core_grp = TempWS + "\\core_grp.img"
    gp.RegionGroup_sa("core1_", core_grp, "EIGHT", "WITHIN")
    
    # convert core groups to txt file...
    coreGrpFile = "%s\\coreGrpFile.txt" % TempWS
    gp.RasterToASCII_conversion(core_grp, coreGrpFile)
    
    # convert 4 class frag map to txt file...
    fragMap_4c = "%s\\fragMap_4c.txt" % TempWS
    gp.RasterToASCII_conversion(fragMap2_f, fragMap_4c)
    
    
    cur = gp.SearchCursor(core_grp)
    row = cur.next()
    
    remap_dct = {}
    
    # for each group...
    while row:
        grpID = row.GetValue("Value")     # group ID
        count = row.GetValue("Count")   # pixel count
    
        # area in hectares...
        # modified by GM from original, original did the calculation in acres. 
        area = count * (cellsize*cf)**2 / 10000
    
        # largest core...
        if area >= 50000:
            remap_dct[grpID] = 7

        # medium core...
        elif 10000 <= area < 50000:
            remap_dct[grpID] = 6

        # medium core...
        elif 1000 <= area < 10000:
            remap_dct[grpID] = 5

        # small core...
        else:
            remap_dct[grpID] = 4
    
        row = cur.next()
    del cur,row
    
    fragMap_6c = "%s\\fragMap_6c.txt" % TempWS
    
    # input grid txt file...
    o_coreGrp = file(coreGrpFile,"r")
    o_fragMap_4c = file(fragMap_4c,"r")       # open file
    o_fragMap_6c = file(fragMap_6c,"w")
    
    # write header lines to output file...
    for x in range(6):
        o_fragMap_6c.write(o_coreGrp.readline())
        o_fragMap_4c.readline()
    
    # reset input grid to start...
    o_coreGrp.seek(0)
    
    # get raster properties...
    ncols = int(o_coreGrp.readline().split(" ")[-1])
    nrows = int(o_coreGrp.readline().split(" ")[-1])
    Xmin = float(o_coreGrp.readline().split(" ")[-1])
    Ymin = float(o_coreGrp.readline().split(" ")[-1])
    cellsize = float(o_coreGrp.readline().split(" ")[-1])
    NoData = o_coreGrp.readline().split(" ")[-1][:-1]
    
    for rowNo in xrange(nrows):
    
        grp_line = o_coreGrp.readline().split(" ")[:-1]
        frag_4c_line = o_fragMap_4c.readline().split(" ")[:-1]
        frag_6c_line = ""
        
        for colNo in xrange(ncols):
    
            grpID = int(grp_line[colNo])
            clss_4c = frag_4c_line[colNo]
    
            # swap perforated for edge (to be consistent with non-SA version)...
            if clss_4c == '2':
                frag_6c_line += "3 "
            # swap edge for perforated (to be consistent with non-SA version)...
            elif clss_4c == '3':
                frag_6c_line += "2 "
            # add in core tract size class...
            elif clss_4c == '4':
                frag_6c_line += "%s " % remap_dct[grpID]
            else:
                frag_6c_line += "%s " % clss_4c
    
        frag_6c_line += "\n"
        o_fragMap_6c.write(frag_6c_line)
    
    
    o_coreGrp.close()
    o_fragMap_4c.close()
    o_fragMap_6c.close()
    
            
    
    # convert classification to final output raster...
    gp.ASCIIToRaster_conversion (fragMap_6c, FragMap, "INTEGER") 
    
    # define raster projection...
    gp.DefineProjection_management (FragMap, spatRef) 
    
    
    #----------------------------------------------------
    # ATTEMPT TO DELETE INTERMEDIATE FILES AND TEMPORARY WORKSPACE...
    

    try:
        a=1
        # comment the line below if you want all the intermediate files to be kept (wanrning  - don't do this if working on many tiles in batch) 
        #gp.delete_management(TempWS)
    
    except:
        print "UNABLE TO DELETE TEMPORARY DATA FOLDER: '%s'" % TempWS
        gp.AddWarning("UNABLE TO DELETE TEMPORARY DATA FOLDER: '%s'" % TempWS)
    
    gp.MakeRasterLayer(FragMap, FragMap_lyr)
    
    '''
    #----------------------------------------------------
    # CREATE DISPLAY LAYER...
    
    # script location...
    script_wksp = os.path.split(sys.argv[0])[0]
    
    # symbology layer file (assumed to be located in same workspace as script)...
    symbology = "%s\\Fragmentation Map Legend.lyr" % script_wksp
    
    # apply symbology laye to display layer...
    gp.ApplySymbologyFromLayer_management (FragMap_lyr, symbology) 
    '''
    
    e = time.clock()
    print "\nTOTAL TIME IS %s MINUTES" % ((e-s)/60)

except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)

    gp.AddError(pymsg)

    print pymsg

    

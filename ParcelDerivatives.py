"""
 SYNOPSIS

     Parcel Derivatives

 DESCRIPTION

    * Combines multiple parcel datasets to create a polygons showing which parcels the City has permits for
    * Extracts parcels with an owner containing Nehemiah
    * Combine certain parcels into one feature class showing which parcels the City is responsible for mowing
    * Finally, clean up any loose data that is no longer needed

 REQUIREMENTS

     Python 3
     arcpy
 """

import arcpy
import os
import traceback
import sys
sys.path.insert(0, "C:/Scripts")
import Logging

# Environment
arcpy.env.overwriteOutput = True

# SDE and FGDB paths
fgdb_services = r"F:\Shares\FGDB_Services"
connections = os.path.join(fgdb_services, "DatabaseConnections")
data = os.path.join(fgdb_services, "Data")
cityworks_view = os.path.join(connections, "DA@mcwintcwdb.cwprod@CityworksView.sde")
cityworks_prod = os.path.join(connections, "DA@mcwintcwdb.cwprod@imSPFLD.sde")
sde = os.path.join(connections, "COSGIS@10.136.40.46@SOA.sde")

# Assessment information Paths
assessment_information = os.path.join(cityworks_prod, "AssessmentInformation")
enterprise_zone = os.path.join(assessment_information, "EnterpriseZone")
tif_districts = os.path.join(assessment_information, "TIFDistrict")

# Reference data paths
reference_data = os.path.join(cityworks_prod, "ReferenceData")
facility_site_point = os.path.join(reference_data, "FacilitySitePoint")

# Parcels inputs and outputs
parcel_owners = os.path.join(sde, "soa.SANGIS.ptinfo1")
cadastral = os.path.join(sde, "soa.SANGIS.Cadastral")
demography = os.path.join(cityworks_prod, "Demography")
census_tracts = os.path.join(demography, "Tract2010Insp")
qualified_census_tracts = os.path.join(demography, "CenTract_Qualified")
parcel_polygons = os.path.join(cadastral, "soa.SANGIS.Parcel_Poly")

# Parcel derivatives paths
parcel_derivatives = os.path.join(data, "ParcelDerivatives.gdb")
parcels = os.path.join(parcel_derivatives, "ParcelPolygons")
parcels_nehemiah_table = os.path.join(parcel_derivatives, "Parcels_Nehemiah_table")
parcels_tsp_table = os.path.join(parcel_derivatives, "Parcels_TSP_table")
parcels_city_table = os.path.join(parcel_derivatives, "Parcels_City_table")
parcels_commercial_table = os.path.join(parcel_derivatives, "Parcels_Commercial_table")
parcels_owner_city = os.path.join(parcel_derivatives, "Parcels_City")
parcels_cwlp = os.path.join(parcel_derivatives, "Parcels_CWLP")
parcels_cospw = os.path.join(parcel_derivatives, "Parcels_COSPW")
parcels_oped = os.path.join(parcel_derivatives, "Parcels_OPED")
parcels_trustee = os.path.join(parcel_derivatives, "Parcels_CountyTrustee")
parcels_poi = os.path.join(parcel_derivatives, "Parcel_POI")
points_surplus_property = os.path.join(parcel_derivatives, "Points_SurplusProperty")

# Permits paths
permits_issued = os.path.join(parcel_derivatives, "Permits_Issued")
permits_CTQ = os.path.join(parcel_derivatives, "Permits_CTQ")
permits_EZ = os.path.join(parcel_derivatives, "Permits_EZ")
permits_TIF = os.path.join(parcel_derivatives, "Permit_TIF")
permits_Wards = os.path.join(parcel_derivatives, "Permits_Wards")
permits_opportunity_zones = os.path.join(parcel_derivatives, "Permits_OpportunityZones")
parcels_permits_issued = os.path.join(parcel_derivatives, "Parcels_PermitsIssued")
parcels_surplus_property = os.path.join(parcel_derivatives, "Parcels_SurplusProperty")

# Other subject parcel paths
parcels_owner_medical_table = os.path.join(parcel_derivatives, "Parcels_Medical_table")
parcels_owner_schools_table = os.path.join(parcel_derivatives, "Parcels_Schools_table")
parcels_owner_state_table = os.path.join(parcel_derivatives, "Parcels_State_table")

# Administrative area paths
admin_area = os.path.join(cityworks_prod, "AdministrativeArea")
admin_area_merged = os.path.join(admin_area, "SPI_Administrative_Areas_Merged")
city_limits = os.path.join(admin_area, "SPI_LIMITS")

# Infrastructure operations paths
infrastructure_operations = os.path.join(cityworks_prod, "InfrastructureOperations")
row = os.path.join(infrastructure_operations, "ROW")
mow_zones = os.path.join(parcel_derivatives, "MowZones")

# List of features to clean up
to_delete = [parcels, permits_CTQ, permits_EZ, permits_TIF, permits_Wards,
             parcels_nehemiah_table, parcels_tsp_table, parcels_city_table,
             parcels_owner_city, parcels_owner_medical_table, parcels_owner_schools_table, parcels_owner_state_table, parcels_commercial_table]


@Logging.insert("Permits to Parcels", 1)
def permits_parcels():
    """Combine different parcels marked with different types of permits into one feature class"""

    # Census Tracts
    Logging.logger.info("------START Permits Issued")
    arcpy.MakeQueryLayer_management(cityworks_view, "Query_PermitsIssued",
                                    "select Shape,ObjectID,CA_OBJECT_ID,CaseNumber,TypeDescription,SubTypeDescription,Status,"
                                    "LOCATION,NAME,ROLE_DESC,TASK_COMPLETE_DATE,BusinessOwner,SUM_PAYMENT_AMOUNT,ASSET_ID_Parcel,"
                                    "VALUE from CityWorksView.dbo.vw_PLL_IssuedPermits", "ObjectID", "POINT", "3436",)
    arcpy.FeatureClassToFeatureClass_conversion("Query_PermitsIssued", parcel_derivatives, "Permits_Issued")
    arcpy.MakeFeatureLayer_management(permits_issued, "Permits_Issued")
    arcpy.MakeFeatureLayer_management(qualified_census_tracts, "CensusTracts")
    arcpy.SpatialJoin_analysis("Permits_Issued", "CensusTracts", permits_CTQ,
                               field_mapping="CA_OBJECT_ID 'CA_OBJECT_ID' true true false 8 Double 0 0,First,#,Permits_Issued,CA_OBJECT_ID,-1,-1;"
                                             f"CaseNumber 'CaseNumber' true true false 20 Text 0 0,First,#,Permits_Issued,CaseNumber,0,20;"
                                             f"TypeDescription 'TypeDescription' true true false 40 Text 0 0,First,#,Permits_Issued,TypeDescription,0,40;"
                                             f"SubTypeDescription 'SubTypeDescription' true true false 40 Text 0 0,First,#,Permits_Issued,SubTypeDescription,0,40;"
                                             f"Status 'Status' true true false 10 Text 0 0,First,#,Permits_Issued,Status,0,10;"
                                             f"LOCATION 'LOCATION' true true false 100 Text 0 0,First,#,Permits_Issued,LOCATION,0,100;"
                                             f"NAME 'NAME' true true false 60 Text 0 0,First,#,Permits_Issued,NAME,0,60;"
                                             f"ROLE_DESC 'ROLE_DESC' true true false 40 Text 0 0,First,#,Permits_Issued,ROLE_DESC,0,40;"
                                             f"TASK_COMPLETE_DATE 'TASK_COMPLETE_DATE' true true false 8 Date 0 0,First,#,Permits_Issued,TASK_COMPLETE_DATE,-1,-1;"
                                             f"BusinessOwner 'BusinessOwner' true true false 60 Text 0 0,First,#,Permits_Issued,BusinessOwner,0,60;"
                                             f"SUM_PAYMENT_AMOUNT 'SUM_PAYMENT_AMOUNT' true true false 8 Double 0 0,First,#,Permits_Issued,SUM_PAYMENT_AMOUNT,-1,-1;"
                                             f"ASSET_ID_Parcel 'ASSET_ID_Parcel' true true false 50 Text 0 0,First,#,Permits_Issued,ASSET_ID_Parcel,0,50;"
                                             f"OBJECTID 'OBJECTID' true true false 4 Long 0 10,First,#,{qualified_census_tracts},OBJECTID,-1,-1;"
                                             f"STATEFP10 'STATEFP10' true true false 2 Text 0 0,First,#,{qualified_census_tracts},STATEFP10,0,2;"
                                             f"COUNTYFP10 'COUNTYFP10' true true false 3 Text 0 0,First,#,{qualified_census_tracts},COUNTYFP10,0,3;"
                                             f"TRACTCE10 'TRACTCE10' true true false 6 Text 0 0,First,#,{qualified_census_tracts},TRACTCE10,0,6;"
                                             f"GEOID10 'GEOID10' true true false 11 Text 0 0,First,#,{qualified_census_tracts},GEOID10,0,11;"
                                             f"NAME10 'NAME10' true true false 7 Text 0 0,First,#,{qualified_census_tracts},NAME10,0,7;"
                                             f"NAMELSAD10 'NAMELSAD10' true true false 20 Text 0 0,First,#,{qualified_census_tracts},NAMELSAD10,0,20;"
                                             f"MTFCC10 'MTFCC10' true true false 5 Text 0 0,First,#,{qualified_census_tracts},MTFCC10,0,5;"
                                             f"FUNCSTAT10 'FUNCSTAT10' true true false 1 Text 0 0,First,#,{qualified_census_tracts},FUNCSTAT10,0,1;"
                                             f"ALAND10 'ALAND10' true true false 8 Double 8 38,First,#,{qualified_census_tracts},ALAND10,-1,-1;"
                                             f"AWATER10 'AWATER10' true true false 8 Double 8 38,First,#,{qualified_census_tracts},AWATER10,-1,-1;"
                                             f"INTPTLAT10 'INTPTLAT10' true true false 11 Text 0 0,First,#,{qualified_census_tracts},INTPTLAT10,0,11;"
                                             f"INTPTLON10 'INTPTLON10' true true false 12 Text 0 0,First,#,{qualified_census_tracts},INTPTLON10,0,12;"
                                             f"CT_2010 'CT_2010' true true false 8 Double 8 38,First,#,{qualified_census_tracts},CT_2010,-1,-1;"
                                             f"Inspector 'Inspector' true true false 30 Text 0 0,First,#,{qualified_census_tracts},Inspector,0,30;"
                                             f"InspUserNa 'InspUserNa' true true false 18 Text 0 0,First,#,{qualified_census_tracts},InspUserNa,0,18;"
                                             f"SID 'SID' true true false 8 Double 8 38,First,#,{qualified_census_tracts},SID,-1,-1;"
                                             f"GlobalID 'GlobalID' true true false 38 Text 0 0,First,#,{qualified_census_tracts},GlobalID,0,38;"
                                             f"Shape_STAr 'Shape_STAr' true true false 8 Double 8 38,First,#,{qualified_census_tracts},Shape_STAr,-1,-1;"
                                             f"Shape_STLe 'Shape_STLe' true true false 8 Double 8 38,First,#,{qualified_census_tracts},Shape_STLe,-1,-1;"
                                             f"GlobalID_1 'GlobalID_1' false false false 38 GlobalID 0 0,First,#,{qualified_census_tracts},GlobalID_1,-1,-1;"
                                             f"VALUE 'VALUE' true true false 255 Text 0 0,First,#,{qualified_census_tracts},VALUE,-1,-1")
    Logging.logger.info("------FINISH Permits Issued")

    # Surplus Properties
    Logging.logger.info("------START Surplus Properties")
    arcpy.MakeQueryLayer_management(cityworks_view, "Query_SurplusProperty",
                                    "select CA_OBJECT_ID,CASE_TYPE,CASE_TYPE_DESC,CASE_NUMBER,CASE_STATUS,LOCATION,STATUS_CODE,CX,CY,PIN,AdminArea,Owner,PropHouseNo,PropDir,PropStreet,PropCity,PropState,"
                                    "PropZip,CensusTract,Sub_Name,Doc_Number,MAPOrdinance,Name,TIFDISTNAME,Objectid,Shape,Ordinance,Assessee,CertNum,INSP,TaxYear,DocNo,SurUse "
                                    "from CityWorksView.dbo.vw_PLL_SurplusProperty", "ObjectID", "POINT", "3436",)
    arcpy.FeatureClassToFeatureClass_conversion("Query_SurplusProperty", parcel_derivatives, "Points_SurplusProperty", "CASE_STATUS IN ('SUR-ACTIVE', 'SUR-PEND')")
    arcpy.MakeFeatureLayer_management(points_surplus_property, "Points_SurplusProperty")
    arcpy.FeatureClassToFeatureClass_conversion(parcel_polygons, parcel_derivatives, "ParcelPolygons")
    arcpy.MakeFeatureLayer_management(parcels, "ParcelPolygons")
    arcpy.SpatialJoin_analysis("ParcelPolygons", "Points_SurplusProperty", parcels_surplus_property, "JOIN_ONE_TO_ONE", "KEEP_COMMON")
    Logging.logger.info("------FINISH Surplus Properties")

    # Enterprise Zone
    Logging.logger.info("------START Enterprise Zone")
    arcpy.MakeFeatureLayer_management(permits_CTQ, "Permits_CTQ")
    arcpy.MakeFeatureLayer_management(enterprise_zone, "EnterpriseZone")
    arcpy.SpatialJoin_analysis("Permits_CTQ", "EnterpriseZone", permits_EZ)
    Logging.logger.info("------FINISH Enterprise Zone")

    # TIF Districts
    Logging.logger.info("------START TIF Districts")
    arcpy.MakeFeatureLayer_management(permits_EZ, "permits_EZ")
    arcpy.MakeFeatureLayer_management(tif_districts, "TIFDistricts")
    arcpy.SpatialJoin_analysis("permits_EZ", "TIFDistricts", permits_TIF)
    Logging.logger.info("------FINISH TIF Districts")

    # Administrative Areas Merged
    Logging.logger.info("------START Administrative Areas Merged")
    arcpy.MakeFeatureLayer_management(permits_TIF, "permits_TIF")
    arcpy.MakeFeatureLayer_management(admin_area_merged, "AdministrativeAreaMerged")
    arcpy.SpatialJoin_analysis("permits_TIF", "AdministrativeAreaMerged", permits_Wards)
    Logging.logger.info("------FINISH Administrative Areas Merged")

    # Census Tracts
    Logging.logger.info("------START Census Tracts")
    arcpy.MakeFeatureLayer_management(permits_Wards, "permits_Wards")
    arcpy.MakeFeatureLayer_management(census_tracts, "CensusTracts")
    arcpy.SpatialJoin_analysis("permits_Wards", "CensusTracts", permits_opportunity_zones)
    Logging.logger.info("------FINISH Census Tracts")

    # Select parcels by location
    selected_parcels = arcpy.SelectLayerByLocation_management("ParcelPolygons", "INTERSECT", permits_issued)

    # Combine the permits and parcel polygons
    Logging.logger.info("------START Opportunity Zones")
    arcpy.MakeFeatureLayer_management(permits_opportunity_zones, "Permits_OpportunityZones")
    arcpy.SpatialJoin_analysis(selected_parcels, "Permits_OpportunityZones", parcels_permits_issued, "JOIN_ONE_TO_MANY")
    Logging.logger.info("------FINISH Opportunity Zones")


@Logging.insert("Nehemiah Parcels", 1)
def nehemiah_parcels():
    """Extracts parcels with an owner name containing Nehemiah"""
    arcpy.TableToTable_conversion(parcel_owners, parcel_derivatives, "Parcels_Nehemiah_table",
                                  r"Owner1 LIKE '%NEHEMIAH AFFORDABLE HOUSING II%' Or "
                                  r"Owner1 LIKE '%NEHEMIAH AFFORDABLE HOUSING LP%' Or "
                                  r"Owner1 LIKE '%NEHEMIAH EXPANSION%' Or "
                                  r"Owner1 LIKE '%NEHEMIAH PSJ LP%'")
    joined_tables = arcpy.AddJoin_management(parcel_polygons, "PIN", parcels_nehemiah_table, "PIN1", "KEEP_COMMON")
    arcpy.FeatureClassToFeatureClass_conversion(joined_tables, parcel_derivatives, "Parcels_Nehemiah")


@Logging.insert("TSP Parcels", 1)
def tsp_parcels():
    """Extracts parcels with an owner name containing TSP (The Springfield Project)"""

    arcpy.TableToTable_conversion(parcel_owners, parcel_derivatives, "Parcels_TSP_table", r"Owner1 LIKE '%TSP%'")
    joined_tables = arcpy.AddJoin_management(parcel_polygons, "PIN", parcels_tsp_table, "PIN1", "KEEP_COMMON")
    arcpy.FeatureClassToFeatureClass_conversion(joined_tables, parcel_derivatives, "Parcels_TSP")


@Logging.insert("City Parcels", 1)
def city_parcels():
    """Extracts parcels owned by the City of Springfield then splits into new feature classes by owner organization"""
    arcpy.TableToTable_conversion(parcel_owners, parcel_derivatives, "Parcels_City_table", "MTGCode = 26 Or MTGCODE =66 Or MTGCode = 72 Or MTGCode = 73 Or Owner1 = 'SANGAMON COUNTY TRUSTEE'",
                                  fr"tmppin 'tmppin' true false false 8 Double 0 11,First,#,{parcel_owners},-1,-1;"
                                  fr"Owner1 'Owner1' true false false 30 Text 0 0,First,#,{parcel_owners},Owner1,0,30;"
                                  fr"MTGCode 'MTGCode' true true false 2 Short 0 5,First,#,{parcel_owners},MTGCode,-1,-1;"
                                  fr"PIN1 'PIN1' true true false 11 Text 0 0,First,#,{parcel_owners},PIN1,0,11")
    joined_tables = arcpy.AddJoin_management(parcel_polygons, "PIN", parcels_city_table, "PIN1", "KEEP_COMMON")
    arcpy.FeatureClassToFeatureClass_conversion(joined_tables, parcel_derivatives, "Parcels_City")
    arcpy.Select_analysis(parcels_owner_city, parcels_cwlp, "SubjectParcels.MTGCode = 26 Or SubjectParcels.MTGCode = 66")
    arcpy.Select_analysis(parcels_owner_city, parcels_cospw, "SubjectParcels.MTGCode = 72")
    arcpy.Select_analysis(parcels_owner_city, parcels_oped, "SubjectParcels.MTGCode = 73")
    arcpy.Select_analysis(parcels_owner_city, parcels_trustee, "SubjectParcels.Owner1 = 'SANGAMON COUNTY TRUSTEE'")


@Logging.insert("Other Parcels", 1)
def other_parcels():
    """Creates parcels for special types of owners like hospitals, schools, and State owned parcels"""
    # Medical
    arcpy.TableToTable_conversion(parcel_owners, parcel_derivatives, "Parcels_Medical_table",
                                  "soa.SANGIS.ptinfo1.Owner1 LIKE '%MEMORIAL HEALTH SYSTEM%' Or "
                                  "soa.SANGIS.ptinfo1.Owner1 LIKE '%SIU SCHOOL OF MEDICIN%' Or "
                                  "soa.SANGIS.ptinfo1.Owner1 LIKE '%ST JOHNS%' Or "
                                  "soa.SANGIS.ptinfo1.Owner1 LIKE '%SPRINGFIELD CLINIC%' Or "
                                  "soa.SANGIS.ptinfo1.Owner1 LIKE '%Springfield Hospital%' Or "
                                  "soa.SANGIS.ptinfo1.Owner2 LIKE '%MCFARLAND MENTAL HEALTH%' Or "
                                  "soa.SANGIS.ptinfo1.Owner2 LIKE '%Public Health Facility%' Or "
                                  "soa.SANGIS.ptinfo1.Owner1 LIKE '%Central Counties Health%'")
    joined_tables = arcpy.AddJoin_management(parcel_polygons, "PIN", parcels_owner_medical_table, "PIN1", "KEEP_COMMON")
    arcpy.FeatureClassToFeatureClass_conversion(joined_tables, parcel_derivatives, "Parcels_Medical")

    # Schools
    arcpy.TableToTable_conversion(parcel_owners, parcel_derivatives, "Parcels_Schools_table",
                                  "soa.SANGIS.ptinfo1.Owner2 LIKE '%186%' Or "
                                  "soa.SANGIS.ptinfo1.Owner1 LIKE '%186%' Or "
                                  "soa.SANGIS.ptinfo1.Owner1 LIKE '%Sacred Heart%' Or "
                                  "soa.SANGIS.ptinfo1.Owner2 LIKE '%Sacred Heart%' Or "
                                  "soa.SANGIS.ptinfo1.Owner1 LIKE '%ST AGNES%' Or "
                                  "soa.SANGIS.ptinfo1.Owner2 LIKE '%ST AGNES%' Or "
                                  "soa.SANGIS.ptinfo1.Owner2 LIKE '%Christ the King%' Or "
                                  "soa.SANGIS.ptinfo1.Owner1 LIKE '%Lincoln Land Community%' Or "
                                  "soa.SANGIS.ptinfo1.Owner1 LIKE '%U of IL At%' Or "
                                  "soa.SANGIS.ptinfo1.Owner1 LIKE '%Capital Area Career Center%'")
    joined_tables = arcpy.AddJoin_management(parcel_polygons, "PIN", parcels_owner_schools_table, "PIN1", "KEEP_COMMON")
    arcpy.FeatureClassToFeatureClass_conversion(joined_tables, parcel_derivatives, "Parcels_Schools")

    # State of Illinois
    arcpy.TableToTable_conversion(parcel_owners, parcel_derivatives, "Parcels_State_Table",
                                  "soa.SANGIS.ptinfo1.Owner1 = 'STATE OF ILLINOIS' And "
                                  "soa.SANGIS.ptinfo1.Owner2 LIKE '%SECRETARY%'")
    joined_tables = arcpy.AddJoin_management(parcel_polygons, "PIN", parcels_owner_state_table, "PIN1", "KEEP_COMMON")
    arcpy.FeatureClassToFeatureClass_conversion(joined_tables, parcel_derivatives, "Parcels_State")

    # Commercial
    arcpy.TableToTable_conversion(parcel_owners, parcel_derivatives, "Parcels_Commercial_table", "soa.SANGIS.ptinfo1.ClassCode IN ('50', '60')")
    joined_tables = arcpy.AddJoin_management(parcel_polygons, "PIN", parcels_commercial_table, "PIN1", "KEEP_COMMON")
    arcpy.FeatureClassToFeatureClass_conversion(joined_tables, parcel_derivatives, "Parcels_Commercial")


@Logging.insert("POI Parcels", 1)
def poi_parcels():
    """Takes the facility site points layer and grabs the parcels they fall on as a separate layer"""
    arcpy.SpatialJoin_analysis(parcel_polygons, facility_site_point, parcels_poi, "JOIN_ONE_TO_ONE", "KEEP_COMMON")


@Logging.insert("Mowing Parcels", 1)
def mowing_parcels():
    """Combines all the relevant parcels into one feature class showing plots the City mows"""
    arcpy.FeatureClassToFeatureClass_conversion(row, parcel_derivatives, "MowZones")

    """# Append county trustee parcels
    selected_city_parcels = arcpy.SelectLayerByLocation_management(parcels_trustee, "HAVE_THEIR_CENTER_IN", city_limits)
    arcpy.Append_management(selected_city_parcels, mow_zones, "NO_TEST",
                            fr"ItemNo 'ItemNo' true true false 2 Short 0 0,First,#;"
                            fr"Use_ 'Use_' true true false 50 Text 0 0,First,#;"
                            fr"Description 'Desc' true true false 50 Text 0 0,First,#,{parcels_trustee},Owner1,0,30"
                            fr"DateAdded 'DateAdded' true true false 8 Date 0 0,First,#;"
                            fr"Misc 'Misc' true true false 50 Text 0 0,First,#;"
                            fr"MowedBy 'MowedBy' true true false 50 Text 0 0,First,#;"
                            fr"GlobalID 'GlobalID' false false true 38 GlobalID 0 0,First,#;"
                            fr"Date1 'Date1' true true false 8 Date 0 0,First,#;"
                            fr"Date2 'Date2' true true false 8 Date 0 0,First,#;"
                            fr"Nbr1 'Nbr1' true true false 8 Double 0 0,First,#;"
                            fr"Nbr2 'nbr2' true true false 8 Double 0 0,First,#;"
                            fr"Test1 'Test1' true true false 15 Text 0 0,First,#;"
                            fr"Test2 'Test2' true true false 25 Text 0 0,First,#;"
                            fr"FacilityID 'Facility Identifier' true true false 50 Text 0 0,First,#,P{parcels_trustee}e,PIN,0,255;"
                            fr"NAD83X 'Easting(X)' true true false 8 Double 0 0,First,#;"
                            fr"NAD83Y 'Northing(Y)' true true false 8 Double 0 0,First,#;"
                            fr"Status 'Status' true true false 50 Text 0 0,First,#;"
                            fr"Lbl 'Lbl' true true false 50 Text 0 0,First,#")

    # Append surplus property parcels
    selected_surplus_property_parcels = arcpy.SelectLayerByLocation_management(parcels_surplus_property, "HAVE_THEIR_CENTER_IN", city_limits)
    arcpy.Append_management(selected_surplus_property_parcels, mow_zones, "NO_TEST")"""

    # Calculate fields
    arcpy.CalculateField_management(mow_zones, "MowedBy", "'PW'")
    """selected_county_trustee_parcels = arcpy.SelectLayerByAttribute_management(mow_zones, "NEW_SELECTION", "Description LIKE '%SANGAMON COUNTY TRUSTEE%'")
    arcpy.CalculateFields_management(selected_county_trustee_parcels, "PYTHON3", [["Use_", "'PARCEL'"], ["MowedBy", "'CONT'"]])
    selected_surplus_property_parcels = arcpy.SelectLayerByAttribute_management(mow_zones, "NEW_SELECTION", "Use_ LIKE '%Vacant Lot%'")
    arcpy.CalculateFields_management(selected_surplus_property_parcels, "PYTHON3", [["Description", "'Vacant Lot'"], ["MowedBy", "'CONT'"]])"""


@Logging.insert("Cleanup", 1)
def cleanup():
    """Cleanup data that is no longer needed"""
    for feature_class in to_delete:
        arcpy.Delete_management(feature_class)


if __name__ == "__main__":
    traceback_info = traceback.format_exc()
    try:
        Logging.logger.info("Script Execution Started")
        permits_parcels()
        nehemiah_parcels()
        tsp_parcels()
        city_parcels()
        other_parcels()
        poi_parcels()
        mowing_parcels()
        cleanup()
        Logging.logger.info("Script Execution Finished")
    except (IOError, NameError, KeyError, IndexError, TypeError, UnboundLocalError, ValueError):
        Logging.logger.info(traceback_info)
    except NameError:
        print(traceback_info)
    except arcpy.ExecuteError:
        Logging.logger.error(arcpy.GetMessages(2))
    except:
        Logging.logger.info("An unspecified exception occurred")

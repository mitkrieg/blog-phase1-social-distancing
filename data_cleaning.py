import pandas as pd
import numpy as np

#Parks Patrol: data collected from Urban Park Rangers and the Parks Enforcement Patrol

#Read csv file and reconcile type issues
patrol = pd.read_csv('data/Parks_Patrol.csv', 
                     dtype={'simplified_encounter_type': str, 'closed_patroncount': str,
                           'closed_education': str, 'closed_outcome_spec': str, 'closed_outcome': str,
                           'closed_pdcontact': str,'sd_amenity': str, 'closed_amenity': str, 'sd_pdcontact': str})

#Drop unneeded columns
patrol.drop(['summonscount_a01','summonscount_a03','summonscount_a04','summonscount_a22',
             'other_summonscount', 'closed_amenity', 'closed_patroncount', 'closed_education',
             'closed_outcome', 'closed_pdcontact', 'closed_outcome_spec',
             'patrol_method', 'visit_reason'], axis=1, inplace=True)

#Drop missing values & non-encounters
patrol.drop(patrol.loc[patrol.simplified_encounter_type == 'No Encounter'].index,inplace=True)
patrol.dropna(axis=0,subset=['sd_patronscomplied'],inplace= True)

#match dataframes and list source
patrol.rename(columns={'park_division':'city_agency'},inplace=True)
patrol['source'] = 'patrol'

##################################
#Parks Ambassador: data collected from Social Distancing Ambassadors 
#Read csv file and reconcile type issues
sda = pd.read_csv('data/Parks_Ambassador.csv',
                 dtype={'simplified_encounter_type': str, 'closed_patroncount': str,
                           'closed_education': str, 'closed_outcome_spec': str, 'closed_outcome': str,
                           'closed_pdcontact': str,'sd_amenity': str, 'closed_amenity': str, 'sd_pdcontact': str})

#Drop unneeded columns
sda.drop(['closed_amenity', 'closed_patroncount','closed_outcome', 'closed_approach', ], axis=1, inplace=True)

#Drop missing values & non-encounters
sda.drop(sda.loc[sda.simplified_encounter_type == 'No Encounter'].index,inplace=True)
sda.dropna(axis=0,subset=['sd_patronscomplied'],inplace= True)

#match dataframes and list source
sda.rename(columns={'park_division':'city_agency'},inplace=True)
sda['source'] = 'sda'


##################################
# City Wide Amabassador: data collected from Interagency Ambassadors
# read csv
citywide = pd.read_csv('data/Citywide.csv',
                 dtype={'simplified_encounter_type': str, 'closed_patroncount': str,
                           'closed_education': str, 'closed_outcome_spec': str, 'closed_outcome': str,
                           'closed_pdcontact': str,'sd_amenity': str, 'closed_amenity': str, 'sd_pdcontact': str})

#Drop unneeded columns
citywide.drop(['closed_amenity', 'closed_patroncount','closed_outcome', 'closed_approach', ], axis=1, inplace=True)

#Drop missing values & non-encounters
citywide.dropna(axis=0,subset=['sd_patronscomplied'],inplace= True)

# list source
citywide['source'] = 'citywide'

#####################
# Parks Crowds Data: data collected from NYC Parks Maintenance & Operations staff 
#read csv 
mando = pd.read_csv('data/Maintenance_and_operations.csv')

mando.drop(['park_district'], axis=1, inplace=True)

mando['source'] = pd.Series(['mando' for x in range(0,mando.shape[0])])
mando.drop(mando.loc[mando.action_taken == 'Did not approach the crowd; the crowd remains'].index,inplace=True)
#mando.dropna(axis=0,subset=['sd_patronscomplied'],inplace= True)

mando.rename(columns={'amenity':'sd_amenity','action_taken':'encounter_type',
                      'encounter_timestamp':'encounter_datetime'},inplace= True)

mando['sd_patronscomplied'] = 0
mando['sd_patronsnocomply'] = 0

mando.sd_patronsnocomply = np.where(mando.encounter_type == 'Approached the crowd; they ignored the employee',
                                 mando.patroncount,0)
mando.sd_patronscomplied = np.where(mando.encounter_type == 'Approached the crowd; they complied with instructions',
                                 mando.patroncount,0)

mando['source'] = 'mando'

#collecting all data into into a single dataframe using pd.concat
frames = [patrol,citywide,sda,mando]
nyc_sd = pd.concat(frames,sort=True,ignore_index=True)
nyc_sd.dropna(axis=0, subset=['sd_patronscomplied','sd_patronsnocomply'],inplace=True) #drop missing social distancing values
comply = nyc_sd.drop(nyc_sd.loc[(nyc_sd.sd_patronscomplied == 0)&(nyc_sd.sd_patronsnocomply == 0)].index)


#clean amenity fields
conditions = [
    nyc_sd['sd_amenity'] == 'Handall court',
    nyc_sd['sd_amenity'] == 'Skate Park',
    nyc_sd['sd_amenity'] == 'Tennis court',
    nyc_sd['sd_amenity'] == 'Parking Lot',
    nyc_sd['sd_amenity'] == 'Softball field',
    nyc_sd['sd_amenity'] == 'Open field/multi-purpose play area',
    nyc_sd['sd_amenity'] == 'Adult fitness equipment',
]

choices = [
    'Handball court',
    'Skate park',
    'Tennis courts',
    'Parking lot',
    'Baseball field',
    'Open field',
    'Fitness equipment'
]

nyc_sd['sd_amenity'] = np.select(conditions,choices,default=nyc_sd.sd_amenity)

#prepare geo infomation
import geopandas as gpd
from shapely import wkt

#read areas csv and turn multipolygons into shapefiles
areas = gpd.read_file('data/areas.csv')
areas['multipolygon'] = areas['multipolygon'].apply(wkt.loads) #changes multipolygon string to multipolgyon shape

#join areas with sd dataframes
nyc_sd_area = nyc_sd.merge(areas, on='park_area_id',how='left')

#read Borough shapes
boros = gpd.GeoDataFrame.from_file('./Borough Boundaries/')

#load dataframes into geopandas and identify geometry
geo_nyc_sd = gpd.GeoDataFrame(nyc_sd_area, geometry='multipolygon')
geoareas = gpd.GeoDataFrame(areas, geometry='multipolygon')

#unify coordinate reference systems onto Borough's 
areas.set_crs(epsg=4326, inplace=True)
geoareas.set_crs(epsg=4326, inplace=True)
geo_nyc_sd.set_crs(epsg=4326, inplace=True)

geoareas = geoareas.to_crs(boros.crs)
geo_nyc_sd = geo_nyc_sd.to_crs(boros.crs)

#group by park_area_id to collect information about each area
listened = geo_nyc_sd.groupby(['park_area_id']).sd_patronscomplied.sum()
ignored = geo_nyc_sd.groupby(['park_area_id']).sd_patronsnocomply.sum()

geoareas = pd.merge(geoareas, listened, on = 'park_area_id',how='left')
geoareas = pd.merge(geoareas, ignored, on = 'park_area_id',how='left')

#clean remaining data
geoareas.sd_patronscomplied = np.where(geoareas.sd_patronscomplied.isna(),0,geoareas.sd_patronscomplied)
geoareas.sd_patronsnocomply = np.where(geoareas.sd_patronsnocomply.isna(),0,geoareas.sd_patronsnocomply)

to_drop = list(geoareas[(geoareas.park_area_desc.str.contains('Central Park'))&
         (geoareas.sd_patronsnocomply == 0)&(geoareas.sd_patronscomplied == 0)].index)

geoareas.drop(index=to_drop,inplace=True)

#calculate sd_percentages
geoareas['sd_percent'] = geoareas.sd_patronscomplied/(geoareas.sd_patronsnocomply+geoareas.sd_patronscomplied)
geoareas['sd_percent_not'] = geoareas.sd_patronsnocomply/(geoareas.sd_patronsnocomply+geoareas.sd_patronscomplied)

import json
#get the file .js

def get_file(data_file):
    # with open(input("Enter the path of the file : "),'r') as dataFile:
    with open(data_file,'r') as dataFile:
        data = dataFile.read()
        obj = data[data.find('{') : data.rfind('}')+1]
        survey_metadata = json.loads(obj)
    return survey_metadata

def segregation(survey_metadata):
    
    job_no = ''
    engineer_name=''
    station_name = ''
    op_volt=''
    my_list = survey_metadata['Trend']
    if len(my_list):
        scanned_date = my_list[0]['date']
        print(f'Scanned Date {scanned_date}')
    else :
        scanned_date =""
        print('Scanned Date not found')

    #get the values of survey fields key
    my_list = survey_metadata['survey_fields']
    if len(my_list):
        # check and get job number
        if my_list[0]['fields'][0]['fieldname'] == '$JOB_NO':
            job_no = my_list[0]['fields'][0]['data']
        else:
            print('job not found')
            job_no =""
    else :
        job_no =0
    #check and get engineer name
    if my_list[0]['fields'][1]['fieldname'] == '$ENGINEER_NAME':
        engineer_name = my_list[0]['fields'][1]['data']
    else: 
        print('engineer_name not found')
        engineer_name=""

    #check and get station name
    if my_list[1]['fields'][0]['fieldname'] == '$SUB_NAME':
        station_name = my_list[1]['fields'][0]['data']
    else: 
        print('station name no found')
        station_name= ""


    #operating voltage kV
    if my_list[2]['fields'][4]['fieldname'] == '$SWGR_OPERATING_V':
        op_volt = my_list[2]['fields'][4]['data']
    else: 
        print('operating voltage not found')
        op_volt=""

    survey_data = {
        'Scanned Date' : scanned_date,
        'Job Number' : str(job_no), 'Engineer Name': engineer_name,
        'Station Name' : station_name, 'Operating Voltage (kV)' : str(op_volt)}
    
    return survey_data

#get the file .js
#data_file=input("Enter the path of the file : ")

#call the get_file function and it returns the value for measurement_data which is used in segregation fucntion
#survey_metadata = get_file(data_file)

#segragation funciton and assign the value to measurement1
#survey_data =segregation(survey_metadata)

# value received from function
#print(survey_data)
import json

def get_file_measurement(data_file):
    # with open(input("Enter the path of the file : "),'r') as dataFile:
    with open(data_file,'r') as dataFile:
        data = dataFile.read()
        obj = data[data.find('{') : data.rfind('}')+1]
        measurement_metadata = json.loads(obj)
    return measurement_metadata


def segregation_measurement(measurement_metadata):
    my_list = measurement_metadata['measurement_fields']
    component = ''
    sublocation = ''
    phasereflock = ''
    db = ''
    #component value check
    if my_list[0]['fields'][2]['fieldname'] == '$COMPONENT':  
        component=my_list[0]['fields'][2]['data']
        if '$' in component:
            component=component.replace('$','') 
    else:
        print('component not found')
    #sublocation
    if my_list[0]['fields'][3]['fieldname'] == '$SUB_LOC':
        sublocation=my_list[0]['fields'][3]['data']        
        if '$' in sublocation:
            sublocation=sublocation.replace('$','') 
    else:
        print('sublocation not found')
    #phase ref lock
    if my_list[1]['fields'][4]['fieldname'] == '$PHASE_REF_LOCK':
        phasereflock = my_list[1]['fields'][4]['data'] 
        if '$' in phasereflock:
            phasereflock=phasereflock.replace('$','') 
    else:
        print('phasereflock not found')

    #measure db
    # incase of ultrasonic 
    #if my_list[1]['fields'][0]['fieldname'] == '$MEASURE_DB' or my_list[1]['fields'][0]['fieldname'] == '$MEASURE_DBUV' :
    #default
    if my_list[1]['fields'][0]['fieldname'] == '$MEASURE_DB' or my_list[1]['fields'][0]['fieldname'] == '$MEASURE_PC'  :
        db = my_list[1]['fields'][0]['data']
    else: 
        print('db not found')

    #store all the fetched values as dict
    measurement = {'component': component, 'sublocation': sublocation, 'phasereflock': phasereflock, 'db': db}
    
    return measurement

#get the file .js
#data_file=input("Enter the path of the file : ")

#call the get_file function and it returns the value for measurement_data which is used in segregation fucntion
#measurement_metadata = get_file(data_file)

#segragation funciton and assign the value to measurement1
#measurement_data =segregation(measurement_metadata)

# value received from function
#print(measurement_data)



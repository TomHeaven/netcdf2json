import json

#file_path = '20140131-surface-currents-oscar-0.33.json'
file_path = '20211231-surface-currents-oscar-0.25.json'
with open(file_path, 'r') as f:
    data_json = json.load(f)
    data = data_json[0]
    print('keys', data.keys())
    print('header', data['header'])
    real_data = tuple(filter(lambda x: x is not None, data['data']))
    print('data len', len(data['data']))
    print('real_data len', len(real_data))
    print('data', data['data'][22], data['data'][23])
    
    print('data_json[1]', data_json[1].keys())
    print('header', data_json[1]['header'])
import os
import json

def to_byte(string):
   try:
      b = string.encode('utf-8')
   except AttributeError:
      b = string
   return b

def read_json(path):
   with open(path, 'r') as f:
      jf = json.loads(f.read())
   return jf

def print_json(j_dict):
   parsed = {k:v.__str__() for k,v in j_dict.items()}
   return json.dumps(parsed, indent=3)

def import_template(path, name, contents=False):
   json_path = os.path.join(path, name)
   json_path = json_path + '.json'
   json_dict = read_json(json_path)
   if contents:
      json_dict = json_dict['Contents']

   return json_dict

if __name__ == "__main__":
   jf = read_json('/Users/lhleung/Documents/Code/data-marketplace-server/data_marketplace/tx_templates/v1.0/s3_certificate.json')
   print(jf)
   print(type(jf))
from itertools import product

rounds = 5
sym_keys = (
   "1e7dor4xpip9isxo",\
   "m2x0ihmzuw3coo91jwbtmqyiaiply3iv", \
)
asy_len = (
   2048, \
   4096, \
)
size = [s for s in range(0,30,5)]
size.append(26)

products = list(product(sym_keys, asy_len, size))

public_key = './instance/client/public-{}.pem'
private_key = './instance/client/private-{}.pem'
file_path = './_file/client/raw/{}.txt'
test_path = './tests/test_aes{sym_len}_rsa{rsa_len}_s{size}.py'
all_test = []

# print(products)
with open('./tests/test_data_registration.template', 'r') as f:
   template = f.read()

print(template)
for key_str, length, size in products:
   print (key_str, length, size)
   size_str = str(size) 
   maps = { 
       'sym_len':str(len(key_str)*8),
       'rsa_len':str(length),
       'size':size_str,
       'sym':key_str,
       'pub_key_path':public_key.format(length),
       'priv_key_path':private_key.format(length),
       'fpath':file_path.format(2**size),
       'rounds':str(rounds)
   }

   wpath = test_path.format(**maps)
   all_test.append(wpath)
   output = template.format(**maps)
   with open(wpath, 'w') as f:
      f.write(output)


with open('./expected_test.txt', 'w') as f:
   f.write('\n'.join(all_test))

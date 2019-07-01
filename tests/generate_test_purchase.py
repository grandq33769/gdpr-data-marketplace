from itertools import product

rounds = 1
size = [s for s in range(0,30,5)]
size.append(26)
size.append(27)
txs = [
    'BSWXRHSIQCZJWLNDOHKNYBGLIARZR9ZT9GKXKHGKDUYPHVOHSFERWORYEYJJIAPTKYC9KRPWLLTXFYVTZ', \
    'IZZSGUEOOXZBXJEW9LFIHJW9XKGZNATQGKLXBKPQPZEGFBGYZYHNCCMQGQ9YCIFYZQPEEHHELZB9WPEVW', \
    'YXLEIKIUKYOZDUSPNLVVZRGKNCYJXSIRU9IEHVSZYW9AANFKFSHJE9VNAKLBBYUFWRASNLQD9EIEBRUFW', \
    'QCPWFSJUGBIWKEADQJUCITUWICLJIQFHNQGRJWSLJYBLRFKWPKSTTCIQKNCXWUGBWHSVITDCKERZAVKUW', \
    'F99VDHRJQB9AJNGLEYPJXJTFBCXAMCKYRNTZDKEEIYYDUYPCDWYKTAVGEFNV9DRKXIQKJNZLERSLY9JZ9', \
    'TYHFASRSJL9RCKZJUI9WUK9RLGFNLIQWBOIHOIRJWCKQTZNTK9CYODRBRDSGIALVGLQKJZCVETAZCPGZW', \
    'NIPTCOYEHRBGAAKHHWZJWUNSLZAUP9EVZLGLDDGLZKANNLXTHJKQUGLTSR9LLXAKFLILCBAUGYXRKRQS9', \
    'NHLAKQKRGXVIRAQZHLONZFXXQDNWQJZOGVFKKCZBRYIEFSEX9IFTYJOADOVDIQ9LLTKUPQYZWCCHHNFVD', \
]

products = size

test_path = './tests/test_data_purchase_s{size}.py'
all_test = []

# print(products)
with open('./tests/test_data_purchase.template', 'r') as f:
   template = f.read()

print(template)
for idx, size in enumerate(products):
   print (idx, size)
   size_str = str(size) 
   maps = { 
       'size':size_str,
       'tx_hash': txs[idx],
       'rounds': str(rounds)
   }

   wpath = test_path.format(**maps)
   all_test.append(wpath)
   output = template.format(**maps)
   with open(wpath, 'w') as f:
      f.write(output)


with open('./expected_test.txt', 'w') as f:
   f.write('\n'.join(all_test))

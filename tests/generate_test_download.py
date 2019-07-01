from itertools import product

rounds = 1
size = [s for s in range(0,30,5)]
size.append(26)
size.append(27)
txs = [
    'PHEUBPROBWQSIEDWPV9COQDQPAAVTFIH9TZTROJJTVCKCVRM9AEVWMHOSOOPEEDYHBWMTDFCISJD99999', \
    'EFLCIDVYIDZOLDUAHFWEVVHDBKEEIXBPEGDYQKJQ9CEWTKTODRWMSCMCNGBHDCKC9POZCKKQEOZNZ9999', \
    'GLKTXPSDYCVRRZKIZPKGXHFCGHP9WMHIGUBHSXEU9YQEHYUTXIQHTSQXEPTGRU9EFSZYB9WDEZBHA9999', \
    'AQVUYTAO9VXAJNJOIPXUJURKFFNEEYPEHJKECCVNPBSTXMRQQWLDTYGVMVEBNBNPFYZKLDJCVCAJ99999', \
    'FEZDIDAWMCX9CQWBCYCADUBWZBPYGVRDTN9ZPNUZGOCRGXBZZUZZXIOJVOOYP9UHPBYCQVDTLSHS99999', \
    'LIVEEYPYU9ADKGOQAUFLSEQQSZBVSCKCSAOWJSOKRJINZLNZMOBJMNVNMWASX9NYLVULRDN9SEHQA9999', \
    'LWXMPTVFRRPBW9IFARPG9ZIXMPWYR9GSITRDNUNNAWFZGCXHQGCT9NWQHWJFFGGCKIYEAMC9PDLNZ9999', \
    'GAHBRGK9AJDAKPDVH9JTNA9TZHXEZPSVYJKBLIGDWMXCKNYUZOFQMPTW9DJ9IYCXYZWFYTCMEWILZ9999', \
]

products = size

test_path = './tests/test_data_download_s{size}.py'
all_test = []

# print(products)
with open('./tests/test_data_download.template', 'r') as f:
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

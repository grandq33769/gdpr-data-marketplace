import pytest

arg = '--benchmark-json=./.benchmarks/{}.json'

with open('./expected_test.txt', 'r') as f:
    test_list = f.read().split('\n')

test_list = list(filter(None, test_list))
print(test_list)
for p in test_list:
    print(p)
    name = p.split('/')[-1].replace('.py', '')
    rarg = arg.format(name)
    pytest.main(['-s', rarg, p])

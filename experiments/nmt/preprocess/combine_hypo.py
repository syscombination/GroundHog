import codecs
import argparse
import re
import json

parser = argparse.ArgumentParser()
parser.add_argument('input_file', nargs='+')
parser.add_argument('output_file')

args = parser.parse_args()
print args.input_file

num_systems = len(args.input_file)
system = []
for i in xrange(num_systems):
	system.append(json.loads(open(args.input_file[i]).read()))
	assert len(system[i]) == len(system[0])

result = []
for i in xrange(len(system[0])):
	for j in xrange(num_systems):
		print len(system[j][i]), 
		if len(system[j][i]) != len(system[0][i]):
			print system[0][i]
			print system[j][i]
		assert len(system[j][i]) == len(system[0][i])
	print ''
	result.append([[system[n][i][k] for n in xrange(num_systems)] for k in xrange(len(system[0][i]))])

output = open(args.output_file, 'w')
output.write(json.dumps(result))
output.close()

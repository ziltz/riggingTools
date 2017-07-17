__author__ = 'Jerry'





def rig_nameGetSide(obj):
	if obj.startswith('l_'):
		return 'l'
	elif obj.startswith('r_'):
		return 'r'
	else:
		return ''


def rig_nameGetMirror(obj):
	if obj.startswith('l_'):
		return 'r'
	elif obj.startswith('r_'):
		return 'l'
	else:
		return ''



def rig_nameMirror(obj):
	tokens = obj.split('_')

	name = ''
	if obj.startswith('l_'):
		name = 'r'
	elif obj.startswith('r_'):
		name = 'l'
	else:
		print 'No side'
		return obj

	for o in tokens[1:]:
		name += '_'+o

	return name

def rig_nameGetBase(obj):
	tokens = obj.split('_')

	print tokens[1:-1]

	checkSide = 1
	if obj.startswith('l_'):
		checkSide = 1
	elif obj.startswith('r_'):
		checkSide = 1
	else:
		checkSide = 0

	newName = ''
	for i in range(checkSide, len(tokens) - 1):

		if i == len(tokens) - 2:
			newName += tokens[i]
		else:
			newName += tokens[i] + '_'

	return newName
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
__author__ = 'Jerry'



def rig_sortListByVectorAxis( _list, axis='x' ):
	for i in range(0, len(_list) ):
		for j in range(0, len(_list)):
			if i == j:
				pass
			else:
				if axis == 'x':
					if _list[i].x < _list[j].x:
						_list[i], _list[j] = _list[j], _list[i]
				if axis == 'y':
					if _list[i].y < _list[j].y:
						_list[i], _list[j] = _list[j], _list[i]
				if axis == 'z':
					if _list[i].z < _list[j].z:
						_list[i], _list[j] = _list[j], _list[i]
	return _list
__author__ = 'Jerry'


import math


def lengthVector( posA, posB):
	dx = posA[0] - posB[0]
	dy = posA[1] - posB[1]
	dz = posA[2] - posB[2]
	return math.sqrt( dx*dx + dy*dy + dz*dz )
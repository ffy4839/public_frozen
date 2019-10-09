import os
import sys
while True:
	print(os.path.abspath(__file__))
	print(os.getcwd()+os.path.sep)
	input()
	sys.exit()

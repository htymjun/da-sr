import numpy as np
import os
import struct
import itertools

def read_fw(name, n, m, l, precision, endian):
    # Open the binary file
    file1 = open(name, 'rb')

    # Skip the first 4 bytes (assuming file record mark)
    file1.seek(4, 0)

    # Define the total number of elements for each field
    ntot_u = (n + 1) * m * l
    ntot_v = n * (m + 1) * l
    ntot_w = n * m * (l + 1)
    ntot = n * m * l

    # Read each field from the binary file
    O1 = np.fromfile(file1, dtype=precision, count=ntot_u)
    file1.seek(8, 1)
    O2 = np.fromfile(file1, dtype=precision, count=ntot_v)
    file1.seek(8, 1)
    O3 = np.fromfile(file1, dtype=precision, count=ntot_w)
    file1.seek(8, 1)
    O4 = np.fromfile(file1, dtype=precision, count=ntot)
    file1.seek(8, 1)
    O5 = np.fromfile(file1, dtype=precision, count=ntot)
    file1.seek(8, 1)
    O6 = np.fromfile(file1, dtype=precision, count=ntot)
    file1.seek(8, 1)
    O7 = np.fromfile(file1, dtype=precision, count=ntot)
    icount = np.fromfile(file1, dtype=np.int64, count=1)
    file1.seek(8, 1)

    # Reshape the fields to the specified dimensions
    O1 = O1.reshape((n + 1, m, l), order='F')
    O2 = O2.reshape((n, m + 1, l), order='F')
    O3 = O3.reshape((n, m, l + 1), order='F')
    O4 = O4.reshape((n, m, l), order='F')
    O5 = O5.reshape((n, m, l), order='F')
    O6 = O6.reshape((n, m, l), order='F')
    O7 = O7.reshape((n, m, l), order='F')

    # Close the file
    file1.close()

    return O1, O2, O3, O4, O5, O6, O7, icount.item()

def fw_to_np(name):
	# path
	script_dir = os.path.dirname(os.path.abspath(__file__))
	name_fw = name+'.fw'
	path_fw = os.path.join(script_dir, name_fw)

	# read mesh information
	name_cn = name+'.cn'
	path_cn = os.path.join(script_dir, name_cn)
	with open(path_cn, 'rb') as file:
		lines = file.readlines()
	# get rid of '\n'
	lines = [line.strip() for line in lines]

	# convert from binary to str
	string = list(range(len(lines)))
	for i in range(len(lines)):
		# remove letters which cannot be read
		string[i] = lines[i].decode('utf-8','ignore')
		if string[i] == 'MTOTAL':
			N = i
		if string[i] == 'XXAXIS':
			Nx = i
		if string[i] == 'YYAXIS':
			Ny = i
		if string[i] == 'ZZAXIS':
			Nz = i
		if string[i] == 'DFITEM':
			Nw = i
	NxNyNz = string[N+1]
	NxNyNz = [float(num) for num in NxNyNz.split()]

	# number of mesh
	n = int(NxNyNz[0])	# x
	m = int(NxNyNz[1])	# y
	l = int(NxNyNz[2])	# z

	# other parameters
	precision = 'float32'
	endian = 'little'

	# read binary file
	u, v, w, p, t, tk, ep, icount = read_fw(path_fw, n, m, l, precision, endian)
	x = read_geometry(string[Nx+1:Ny-1])
	y = read_geometry(string[Ny+1:Nz-1])
	z = read_geometry(string[Nz+1:Nw-1])
	return u, v, w, p, t, icount, x, y, z

def read_geometry(lines):
	for i in range(len(lines)):
		lines[i] = [float(num) for num in lines[i].split()]
	Xi = list(itertools.chain.from_iterable(lines))
	return np.array(Xi)

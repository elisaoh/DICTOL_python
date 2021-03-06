from utils import * 

# inv_IpXY_test()
def ODL_cost(Y, D, X, lambda1):
	"""
	cost = 0.5* ||Y - DX||_F^2 + lambda1||X||_1
	"""
	return  0.5*normF2(Y - np.dot(D, X)) + lambda1*norm1(X)

def ODL_updateD(D, E, F, opts):
	"""
	* The main algorithm in ODL. 
	* Solving the optimization problem:
	  `D = arg min_D -2trace(E'*D) + trace(D*F*D')` subject to: `||d_i||_2 <= 1`,
	     where `F` is a positive semidefinite matrix. 
	* Syntax `[D, iter] = ODL_updateD(D, E, F, opts)`
	  - INPUT: 
	    + `D, E, F` as in the above problem.
	    + `opts`. options:
	      * `opts.max_iter`: maximum number of iterations.
	      * `opts.tol`: when the difference between `D` in two successive 
			iterations less than this value, the algorithm will stop.
	  - OUTPUT:
	    + `D`: solution.
	    + `iter`: number of run iterations.
	-----------------------------------------------
	Author: Tiep Vu, thv102@psu.edu, 04/07/2016
	        (http://www.personal.psu.edu/thv102/)
	-----------------------------------------------
	"""
	def calc_cost(D):
		return -2*np.trace(np.dot(E, D.T)) + np.trace(np.dot(np.dot(F, D.T), D))

	D_old = D.copy() 
	it = 0 
	sizeD = numel(D)
	# print opts.tol
	while it < opts.max_iter:
		it = it + 1 
		for i in xrange(D.shape[1]):
			if F[i,i] != 0:
				a = 1.0/F[i,i] * (E[:, i] - D.dot(F[:, i])) + D[:, i]
				D[:,i] = a/max(LA.norm(a, 2), 1)
		if opts.verbose:
			print 'iter = %3d | cost = %.4f | tol = %f' %(it, calc_cost(D), \
				LA.norm(D - D_old, 'fro')/sizeD )

		if LA.norm(D - D_old, 'fro')/sizeD < opts.tol:
			break 
		D_old = D.copy()
	return D 

def ODL(Y, k, lambda1, opts, method = 'fista'):
	"""
	* Solving the following problem:
	 (D, X) = \arg\min_{D,X} 0.5||Y - DX||_F^2 + lambda1||X||_1
	* Syntax: `(D, X) = ODL(Y, k, lambda1, opts)`
	  - INPUT: 
	    + `Y`: collection of samples.4/7/2016 7:35:39 PM
	    + `k`: number of atoms in the desired dictionary.
	    + `lambda1`: norm 1 regularization parameter.
	    + `opts`: option.
	    + `sc_method`: sparse coding method used in the sparse coefficient update. Possible values:
	      * `'fista'`: using FISTA algorithm. See also [`fista`](#fista).
	      * `'spams'`: using SPAMS toolbox [[12]](#fn_spams). 
	  - OUTPUT:
	    + `D, X`: as in the problem.
	-----------------------------------------------
	Author: Tiep Vu, thv102@psu.edu, 4/7/2016
	        (http://www.personal.psu.edu/thv102/)
	-----------------------------------------------
	"""
	from utils import *
	Y_range = np.array([0, Y.shape[1]])
	D_range = np.array([0, k])
	D = pickDfromY(Y, Y_range, D_range)
	X = np.zeros((D.shape[1], Y.shape[1]))
	if opts.verbose: 
		print 'Initial cost: %5.4f' % ODL_cost(Y, D, X, lambda1)
	it = 0 
	optsX = Opts(max_iter = 300)
	optsD = Opts(max_iter = 200, tol = 1e-8)
	while it < opts.max_iter:
		it += 1 
		# Sparse coding 
		X = lasso_fista(Y, D, X, lambda1, optsX)[0]
		# X = X0[0]
		if opts.verbose: 
			costX = ODL_cost(Y, D, X, lambda1)
			print 'iter: %3d' % it, '| costX = %4.4f' % costX #'it: ', itx
		# Dictionary update
		F = np.dot(X, X.T)
		E = np.dot(Y, X.T) 
		D = ODL_updateD(D, E, F, optsD)
		if opts.verbose:
			costD = ODL_cost(Y, D, X, lambda1)
			print '          | costD = %4.4f' % costD #'it: ', itd
			if abs(costX - costD) < opts.tol:
				break 
	if opts.verbose:
		print 'Final cost: %4.4f' % ODL_cost(Y, D, X, lambda1)
	return (D, X)		

class Opts_ODL:
	def __init__(self, verbose = False, max_iter = 100, tol = 1e-8):
		self.verbose   = verbose
		self.max_iter = max_iter
		self.tol      = tol

def ODL_test():
	d      = 500 # data dimension
	N      = 1000 # number of samples 
	k      = 50 # dictionary size 
	lambda1 = 0.1
	Y      = normc(np.random.rand(d, N))
	D      = normc(np.random.rand(d, k))
	# Xinit  = np.zeros(D.shape[1], Y.shape[1])
	opts = Opts_ODL(max_iter = 100, tol = 1e-8, verbose = True)
	ODL(Y, k, lambda1, opts)

# ODL_test()


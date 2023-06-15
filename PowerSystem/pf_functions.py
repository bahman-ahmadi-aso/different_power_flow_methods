from numpy import ones, r_, conj
from scipy.sparse import csr_matrix, coo_matrix, bmat, csc_matrix, vstack
from scipy.sparse.linalg import spsolve

# from scipy.linalg import inv

import pandas as pd
import numpy as np


def makeYbus(branch_info, bus_info, Sbase, Vbase):
    """Builds the admittance matrix Ybus in p.u.
    and the submatrices needed
    @author: Juan S. Giraldo (UTwente) jnse@ieee.org
    Obs: Slack bus needs to be numbered as 1 !!
    """


    nb = bus_info.shape[0]  ## number of buses
    nl = branch_info.shape[0]  ## number of lines

    sl = bus_info[bus_info['Tb'] == 1]['NODES'].tolist()     # Slack node(s)





    #
    # ## for each branch, compute the elements of the branch admittance matrix where
    # ##
    # ##      | Is |   | Yss  Ysd |   | Vs |
    # ##      |    | = |          | * |    |
    # ##      |-Id |   | Yds  Ydd |   | Vd |
    # ##

    stat = branch_info.iloc[:, 5]  ## ones at in-service branches
    Ys = stat / ((branch_info.iloc[:, 2] + 1j * branch_info.iloc[:, 3]) / (Vbase ** 2 *1000/ Sbase))  ## series admittance
    Bc = stat * branch_info.iloc[:, 4] * (Vbase ** 2*1000 / Sbase)  ## line charging susceptance
    try:
        tap = stat * branch_info.iloc[:, 6]  ## default tap ratio = 1
    except:
        tap = stat * 1

    Ytt = Ys + 1j * Bc / 2
    Yff = Ytt / (tap)
    Yft = - Ys / (tap)
    Ytf = Yft

    ## build connection matrices
    f = branch_info.iloc[:, 0] - 1  ## list of "from" buses
    t = branch_info.iloc[:, 1] - 1  ## list of "to" buses
    ## connection matrix for line & from buses
    Cf = csr_matrix((ones(nl), (range(nl), f)), (nl, nb))
    ## connection matrix for line & to buses
    Ct = csr_matrix((ones(nl), (range(nl), t)), (nl, nb))
    #
    ## build Yf and Yt such that Yf * V is the vector of complex branch currents injected
    ## at each branch's "from" bus, and Yt is the same for the "to" bus end
    i = r_[range(nl), range(nl)]  ## double set of row indices

    Yf = csr_matrix((r_[Yff, Yft], (i, r_[f, t])))
    Yt = csr_matrix((r_[Ytf, Ytt], (i, r_[f, t])))

    ## build Ybus
    Ybus = Cf.T * Yf + Ct.T * Yt        # Full Ybus

    Yss = csr_matrix(Ybus[sl[0]-1, sl[0]-1], shape=(len(sl),len(sl)))
    Ysd = Ybus[0,1:]
    Yds = Ysd.T
    Ydd = Ybus[1:,1:]


    return Yss, Ysd, Yds, Ydd


def run_pf(System_Data_Nodes,PP,QQ, Sbase, Yds, Ydd, V_0):
    nb = System_Data_Nodes.shape[0]  ## number of buses


    P = PP / Sbase
    Q = QQ/ Sbase

    S_nom = (P + 1j * Q).reshape(-1, ).tolist()
    alpha_P = System_Data_Nodes[System_Data_Nodes.Tb != 1].Pct.values.reshape(-1, ).tolist()
    alpha_I = System_Data_Nodes[System_Data_Nodes.Tb != 1].Ict.values.reshape(-1, ).tolist()
    alpha_Z = System_Data_Nodes[System_Data_Nodes.Tb != 1].Zct.values.reshape(-1, ).tolist()


    A = csr_matrix(np.diag(np.multiply(alpha_P, 1. / np.conj(V_0) ** (2)) * np.conj(S_nom)))  # Needs update
    D = csr_matrix((np.multiply(np.multiply(2, alpha_P), 1. / np.conj(V_0)) * np.conj(S_nom)).reshape(-1, 1))  # Needs update

    B = csr_matrix(np.diag(np.multiply(alpha_Z, np.conj(S_nom))) + Ydd)             # Constant
    C = csr_matrix(Yds + (np.multiply(alpha_I, np.conj(S_nom))).reshape(nb-1, 1))   # Constant

    M11 = np.real(A) - np.real(B)
    M12 = np.imag(A) + np.imag(B)
    M21 = np.imag(A) - np.imag(B)
    M22 = -np.real(A) - np.real(B)
    N1 = np.real(C) + np.real(D)
    N2 = np.imag(C) + np.imag(D)
    M = csr_matrix(bmat([[M11, M12], [M21, M22]]))
    N = vstack([N1,N2])
    V = spsolve(M, N)

    return np.add(V[0:nb-1],1j*V[nb-1:])
# # calculate sparsity
# sparsity = 1.0 - np.count_nonzero(A.toarray()) / A.toarray().size
# print(sparsity)
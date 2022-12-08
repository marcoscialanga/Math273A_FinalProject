# -*- coding: utf-8 -*-
"""MATH273Final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10fnY8QG-Z92tCQTdhsfIj0Zcp-1axrC1
"""

import numpy as np
import matplotlib.pyplot as plt
import random
from scipy.linalg import qr
import torch
from torch import nn
from torch.optim import SGD
from matplotlib.pyplot import figure
import math
from numpy import linalg as LA
import numpy as np
import matplotlib.pyplot as plt
from numpy.linalg import matrix_rank

"""Step Size Convergence Code"""

from matplotlib.pyplot import figure
import math
from numpy import linalg as LA
import numpy as np
import matplotlib.pyplot as plt
import random
from scipy.linalg import qr
import torch
from torch import nn
from torch.optim import SGD
from numpy.linalg import matrix_rank

class NeuralNet2(nn.Module):
    
    def __init__(self, N, dList, W = None):
        super(NeuralNet2, self).__init__()
        modules = []
        self.weights = []
        for i in range(N):
          modules.append(nn.Linear(dList[i-1], dList[i], bias = False))
          modules[i].weight.data = torch.nn.Parameter(W[i])
          self.weights.append(modules[i].weight.data)
        self.model = nn.Sequential(*modules)

    def forward(self,x):
        return self.model(x)

#Computes the balance constant
def balanceCheck(X,Y,W,N):
    U, sig, V = np.linalg.svd(X)
    M = (math.sqrt(2)*LA.norm(Y-np.matmul(W,X))+LA.norm(Y))/min(sig)
    return (1/(N*(N+1)**2))*(M**(2/N))
    
#Computes stepsize bound
def stepsize(X,Y,W,N,alpha):
    U, sig, V = np.linalg.svd(X)
    M = (math.sqrt(2)*LA.norm(Y-np.matmul(W,X))+LA.norm(Y))/min(sig)
    delta = (1/(N*(N+1)**2))*(M**(2/N))
    d1 = 2*(1/(1-alpha))*N*(N+1)**2*M**(2-(2/N))*min(sig)**2
    d2 = 2*math.e**(2-(1/N))*N*M**(2-(2/N))*LA.norm(X)**2
    d3 = math.e**(1-(1/N))*N*M**(1-(2/N))*LA.norm(np.matmul(X,Y.T))
    d =d1+d2+d3
    return M/d

class NeuralNet(nn.Module):
    
    def __init__(self, d1, d2, d3, d4):
        super(NeuralNet, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(d1, d2, bias = False),
            nn.Linear(d2, d3, bias = False),
            nn.Linear(d3, d4, bias = False)
        )
        
    def forward(self, x):
        return self.model(x)
    
iterin = 0
works = True


alpha = 0.2 #random alpha value I picked

#while loop checks to ensure that we satisfy all the conditions of the convergence theorem
#x is a random 5x5 matrix
#beta is a diagonal matrix of [1,2,3,4,5]
#y = beta*x + epsilon where epsilon is random noise sampled from gaussian centered at 0 with SD of 0.1
while (iterin < 1000 and works):
    x = np.random.normal(size = (5,5))
    beta = np.diag([1,2,3,4,5])
    y1 = np.matmul(x,beta) 
    epsilon = np.random.normal(0, 0.1, (5,5))
    y = np.add(y1,epsilon)
    model = NeuralNet(5,5,5,5) 
    model = model.float()
    WIlist = []
    for param in model.parameters():
        WIlist.append(param.detach().numpy())
    WI = np.matmul(np.matmul(WIlist[2], WIlist[1]), WIlist[0])
    maxConst = 0
    #maxConst is the max of the matrix multiplications to see what our balance constant needs to be bounded by
    for i in range(0, 1):
        balanceCon = LA.norm(np.matmul(WIlist[i+1].T, WIlist[i+1]) - np.matmul(WIlist[i], WIlist[i].T))
        if maxConst < balanceCon:
            maxConst = balanceCon
    print("iter: ", iterin)
    print("max const: ", maxConst)
    print("balance Constant: ", balanceCheck(x,y,WI,3))
    #Checks to see if we have a positive balance constant for our tuple of weight initializations
    if balanceCheck(x,y,WI,3) > maxConst:
    #Set alpha so that alpha*balanceCheck is the tight bound for the balanced condition
        alpha = maxConst/balanceCheck(x,y,WI,3) 
        works = False
    iterin += 1
    #checks XX^T is full rank
    if matrix_rank(np.matmul(x, x.T)) != 5:
        works = True

#Computes upper bound of stepsize according to Theorem 2.4
step = stepsize(x,y,WI,3,alpha)
print("alpha = ", alpha)
print("stepsize = ", step)

Wlist = []
for param in WIlist:
    Wlist.append(torch.tensor(param))

#Uses the initial weights that satisfies the condition and creates a neural network
W = np.matmul(np.matmul(Wlist[2], Wlist[1]), Wlist[0])
dList = [5,5,5,5]
model = NeuralNet2(3,dList,Wlist)
#Use some step size less than the upperbound to confirm convergence
step = 0.9*step
x = torch.tensor(x).float()
y = torch.tensor(y).float()
iterations = 5000
time = list(range(iterations))
figure(figsize=(8, 6), dpi=80)
#use increasing step sizes to see the first instance of divergence
while True:   
    opt = SGD(model.parameters(), lr = 0.9*step)
    L = nn.MSELoss(reduction = 'sum')

    
    lossList = []
    

    for epoch in range(iterations):
        yhat = model(x)
        loss = L(yhat, y)
        
    # backpropagation
        opt.zero_grad()
        loss.backward()
        opt.step()
        lossList.append(loss.item())
    step = step*2
# convergence to global minimizer
    print(f"Epoch:{epoch} loss is {loss.item()} at step size {step}")
    if math.isnan(loss.item()):
        break
    else:
        stepLegend = "Step: " + str(step)
        plt.plot(time, lossList, label=stepLegend)
plt.legend(loc="upper left")
plt.xlabel("epochs")
plt.ylabel("loss")
plt.title("Loss Function with Different Step Sizes")





class NeuralNet(nn.Module):
    
    def __init__(self, d1, d2, d3, d4):
        super(NeuralNet, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(d1, d2, bias = False),
            nn.Linear(d2, d3, bias = False),
            nn.Linear(d3, d4, bias = False)
        )
        
    def forward(self, x):
        return self.model(x)

countList = []
count = 1000
timeCount = list(range(count))

for i in range(count):
    iterin = 0
    works = True


    alpha = 0.2 #random alpha value I picked

    while (iterin < 1000 and works):
        x = np.random.normal(size = (5,5))
        beta = np.diag([1,2,3,4,5])
        y1 = np.matmul(x,beta) 
        epsilon = np.random.normal(0, 0.1, (5,5))
        y = np.add(y1,epsilon)
        model = NeuralNet(5,5,5,5) 
        model = model.float()
        WIlist = []
        for param in model.parameters():
            WIlist.append(param.detach().numpy())
        maxConst = 0
    #maxConst is the max of the matrix multiplications to see what our balance constant needs to be bounded by
        for i in range(0, 1):
            balanceCon = LA.norm(np.matmul(WIlist[i+1].T, WIlist[i+1]) - np.matmul(WIlist[i], WIlist[i].T))
            if maxConst < balanceCon:
                maxConst = balanceCon
    #Checks to see if we have a positive balance constant for our tuple of weight initializations
        if balanceCheck(x,y,WI,3) > maxConst:
    #Set alpha so that alpha*balanceCheck is the tight bound for the balanced condition
            alpha = maxConst/balanceCheck(x,y,WI,3) 
            works = False
        iterin += 1

#Computes upper bound of stepsize according to Theorem 2.4
    step = stepsize(x,y,WI,3,alpha)
    countList.append(step)


countsList = [round(item, 2) for item in countList]
plt.hist(x=countList, bins='auto', color='#0504aa')
plt.title('Fixed Step Size Convergence Bound')
plt.xlabel('Step Size')
plt.ylabel('Frequency')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

class NeuralNet(nn.Module):
    
    def __init__(self, d1, d2, d3, d4):
        super(NeuralNet, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(d1, d2, bias = False),
            nn.Linear(d2, d3, bias = False),
            nn.Linear(d3, d4, bias = False)
        )
        
    def forward(self, x):
        return self.model(x)
        
countList = []
count = 1000
timeCount = list(range(count))

for i in range(count):
    iterin = 0
    works = True


    alpha = 0.2 #random alpha value I picked

    while (iterin < 1000 and works):
        x = np.random.normal(size = (5,5))
        beta = np.diag([1,2,3,4,5])
        y1 = np.matmul(x,beta) 
        epsilon = np.random.normal(0, 0.1, (5,5))
        y = np.add(y1,epsilon)
        model = NeuralNet(5,2,2,5) 
        model = model.float()
        WIlist = []
        for param in model.parameters():
            WIlist.append(param.detach().numpy())
        maxConst = 0
    #maxConst is the max of the matrix multiplications to see what our balance constant needs to be bounded by
        for i in range(0, 1):
            balanceCon = LA.norm(np.matmul(WIlist[i+1].T, WIlist[i+1]) - np.matmul(WIlist[i], WIlist[i].T))
            if maxConst < balanceCon:
                maxConst = balanceCon
    #Checks to see if we have a positive balance constant for our tuple of weight initializations
        if balanceCheck(x,y,WI,3) > maxConst:
    #Set alpha so that alpha*balanceCheck is the tight bound for the balanced condition
            alpha = maxConst/balanceCheck(x,y,WI,3) 
            works = False
        iterin += 1

#Computes upper bound of stepsize according to Theorem 2.4
    step = stepsize(x,y,WI,3,alpha)
    countList.append(step)


countsList = [round(item, 2) for item in countList]
plt.hist(x=countList, bins='auto', color='#0504aa')
plt.title('Fixed Step Size Convergence Bound')
plt.xlabel('Step Size')
plt.ylabel('Frequency')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

class NeuralNet(nn.Module):
    
    def __init__(self, d1, d2, d3):
        super(NeuralNet, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(d1, d2, bias = False),
            nn.Linear(d2, d3, bias = False)
        )
        
    def forward(self, x):
        return self.model(x)

countList = []
count = 1000
timeCount = list(range(count))

for i in range(count):
    iterin = 0
    works = True


    alpha = 0.2 #random alpha value I picked

    while (iterin < 1000 and works):
        x = np.random.normal(size = (5,5))
        beta = np.diag([1,2,3,4,5])
        y1 = np.matmul(x,beta) 
        epsilon = np.random.normal(0, 0.1, (5,5))
        y = np.add(y1,epsilon)
        model = NeuralNet(5,5,5) 
        model = model.float()
        WIlist = []
        for param in model.parameters():
            WIlist.append(param.detach().numpy())
        maxConst = 0
    #maxConst is the max of the matrix multiplications to see what our balance constant needs to be bounded by
        for i in range(0, 1):
            balanceCon = LA.norm(np.matmul(WIlist[i+1].T, WIlist[i+1]) - np.matmul(WIlist[i], WIlist[i].T))
            if maxConst < balanceCon:
                maxConst = balanceCon
    #Checks to see if we have a positive balance constant for our tuple of weight initializations
        if balanceCheck(x,y,WI,2) > maxConst:
    #Set alpha so that alpha*balanceCheck is the tight bound for the balanced condition
            alpha = maxConst/balanceCheck(x,y,WI,2) 
            works = False
        iterin += 1

#Computes upper bound of stepsize according to Theorem 2.4
    step = stepsize(x,y,WI,2,alpha)
    countList.append(step)


countsList = [round(item, 2) for item in countList]
plt.hist(x=countList, bins='auto', color='#0504aa')
plt.title('Fixed Step Size Convergence Bound')
plt.xlabel('Step Size')
plt.ylabel('Frequency')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

class NeuralNet(nn.Module):
    
    def __init__(self, d1, d2, d3, d4, d5):
        super(NeuralNet, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(d1, d2, bias = False),
            nn.Linear(d2, d3, bias = False),
            nn.Linear(d3, d4, bias = False),
            nn.Linear(d4, d5, bias = False)
        )
        
    def forward(self, x):
        return self.model(x)

countList = []
count = 1000
timeCount = list(range(count))

for i in range(count):
    iterin = 0
    works = True


    alpha = 0.2 #random alpha value I picked

    while (iterin < 1000 and works):
        x = np.random.normal(size = (5,5))
        beta = np.diag([1,2,3,4,5])
        y1 = np.matmul(x,beta) 
        epsilon = np.random.normal(0, 0.1, (5,5))
        y = np.add(y1,epsilon)
        model = NeuralNet(5,5,5,5,5) 
        model = model.float()
        WIlist = []
        for param in model.parameters():
            WIlist.append(param.detach().numpy())
        maxConst = 0
    #maxConst is the max of the matrix multiplications to see what our balance constant needs to be bounded by
        for i in range(0, 1):
            balanceCon = LA.norm(np.matmul(WIlist[i+1].T, WIlist[i+1]) - np.matmul(WIlist[i], WIlist[i].T))
            if maxConst < balanceCon:
                maxConst = balanceCon
    #Checks to see if we have a positive balance constant for our tuple of weight initializations
        if balanceCheck(x,y,WI,4) > maxConst:
    #Set alpha so that alpha*balanceCheck is the tight bound for the balanced condition
            alpha = maxConst/balanceCheck(x,y,WI,4) 
            works = False
        iterin += 1

#Computes upper bound of stepsize according to Theorem 2.4
    step = stepsize(x,y,WI,4,alpha)
    countList.append(step)


countsList = [round(item, 2) for item in countList]
plt.hist(x=countList, bins='auto', color='#0504aa')
plt.title('Fixed Step Size Convergence Bound')
plt.xlabel('Step Size')
plt.ylabel('Frequency')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

class NeuralNet(nn.Module):
    
    def __init__(self, d1, d2, d3, d4, d5):
        super(NeuralNet, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(d1, d2, bias = False),
            nn.Linear(d2, d3, bias = False),
            nn.Linear(d3, d4, bias = False),
            nn.Linear(d4, d5, bias = False)
        )
        
    def forward(self, x):
        return self.model(x)

countList = []
count = 1000
timeCount = list(range(count))

for i in range(count):
    iterin = 0
    works = True


    alpha = 0.2 #random alpha value I picked

    while (iterin < 1000 and works):
        x = np.random.normal(size = (5,5))
        beta = np.diag([1,2,3,4,5])
        y1 = np.matmul(x,beta) 
        epsilon = np.random.normal(0, 0.1, (5,5))
        y = np.add(y1,epsilon)
        model = NeuralNet(5,5,5,5,5) 
        model = model.float()
        WIlist = []
        for param in model.parameters():
            WIlist.append(param.detach().numpy())
        maxConst = 0
    #maxConst is the max of the matrix multiplications to see what our balance constant needs to be bounded by
        for i in range(0, 1):
            balanceCon = LA.norm(np.matmul(WIlist[i+1].T, WIlist[i+1]) - np.matmul(WIlist[i], WIlist[i].T))
            if maxConst < balanceCon:
                maxConst = balanceCon
    #Checks to see if we have a positive balance constant for our tuple of weight initializations
        if balanceCheck(x,y,WI,4) > maxConst:
    #Set alpha so that alpha*balanceCheck is the tight bound for the balanced condition
            alpha = maxConst/balanceCheck(x,y,WI,4) 
            works = False
        iterin += 1

#Computes upper bound of stepsize according to Theorem 2.4
    step = stepsize(x,y,WI,4,alpha)
    countList.append(step)


countsList = [round(item, 2) for item in countList]
plt.hist(x=countList, bins='auto', color='#0504aa')
plt.title('Fixed Step Size Convergence Bound')
plt.xlabel('Step Size')
plt.ylabel('Frequency')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

class NeuralNet(nn.Module):
    
    def __init__(self, d1, d2, d3, d4):
        super(NeuralNet, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(d1, d2, bias = False),
            nn.Linear(d2, d3, bias = False),
            nn.Linear(d3, d4, bias = False)
        )
        
    def forward(self, x):
        return self.model(x)

countList = []
count = 100
timeCount = list(range(count))

for i in range(count):
    iterin = 0
    works = True


    alpha = 0.2 #random alpha value I picked

    while (iterin < 1000 and works):
        x = np.random.normal(size = (5,5))
        beta = np.diag([1,2,3,4,5])
        y1 = np.matmul(x,beta) 
        epsilon = np.random.normal(0, 0.1, (5,5))
        y = np.add(y1,epsilon)
        model = NeuralNet(5,5,5,5) 
        model = model.float()
        WIlist = []
        for param in model.parameters():
            WIlist.append(param.detach().numpy())
        maxConst = 0
    #maxConst is the max of the matrix multiplications to see what our balance constant needs to be bounded by
        for i in range(0, 1):
            balanceCon = LA.norm(np.matmul(WIlist[i+1].T, WIlist[i+1]) - np.matmul(WIlist[i], WIlist[i].T))
            if maxConst < balanceCon:
                maxConst = balanceCon
    #Checks to see if we have a positive balance constant for our tuple of weight initializations
        if balanceCheck(x,y,WI,3) > maxConst:
    #Set alpha so that alpha*balanceCheck is the tight bound for the balanced condition
            alpha = maxConst/balanceCheck(x,y,WI,3) 
            works = False
        iterin += 1

#Computes upper bound of stepsize according to Theorem 2.4
    step = stepsize(x,y,WI,3,alpha)

    Wlist = []
    for param in WIlist:
        Wlist.append(torch.tensor(param))


    W = np.matmul(np.matmul(Wlist[2], Wlist[1]), Wlist[0])
    dList = [5,5,5,5]
    model = NeuralNet2(3,dList,Wlist)
    step = 0.9*step
    x = torch.tensor(x).float()
    y = torch.tensor(y).float() 
    iterations = 5000
    time = list(range(iterations))
    figure(figsize=(8, 6), dpi=80)


    nextIter = True
    while nextIter:   
        opt = SGD(model.parameters(), lr = 0.9*step)
        L = nn.MSELoss(reduction = 'sum')

    
        lossList = []
    

        for epoch in range(iterations):
            yhat = model(x)
            loss = L(yhat, y)
        
    # backpropagation
            opt.zero_grad()
            loss.backward()
            opt.step()
            lossList.append(loss.item())
        step = step*2
# convergence to global minimizer
        if math.isnan(loss.item()):
            nextIter = False
            countList.append(step)
            print(i)

countsList = [round(item, 2) for item in countList]
plt.hist(x=countList, bins='auto', color='#0504aa')
plt.title('Fixed Step Size of Divergence')
plt.xlabel('Step Size')
plt.ylabel('Frequency')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

class NeuralNet(nn.Module):
    
    def __init__(self, d1, d2, d3, d4):
        super(NeuralNet, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(d1, d2, bias = False),
            nn.Linear(d2, d3, bias = False),
            nn.Linear(d3, d4, bias = False)
        )
        
    def forward(self, x):
        return self.model(x)

countList = []
count = 100
timeCount = list(range(count))

for i in range(count):
    iterin = 0
    works = True


    alpha = 0.2 #random alpha value I picked

    while (iterin < 1000 and works):
        x = np.random.normal(size = (5,5))
        beta = np.diag([1,2,3,4,5])
        y1 = np.matmul(x,beta) 
        epsilon = np.random.normal(0, 0.1, (5,5))
        y = np.add(y1,epsilon)
        model = NeuralNet(5,2,2,5) 
        model = model.float()
        WIlist = []
        for param in model.parameters():
            WIlist.append(param.detach().numpy())
        maxConst = 0
    #maxConst is the max of the matrix multiplications to see what our balance constant needs to be bounded by
        for i in range(0, 1):
            balanceCon = LA.norm(np.matmul(WIlist[i+1].T, WIlist[i+1]) - np.matmul(WIlist[i], WIlist[i].T))
            if maxConst < balanceCon:
                maxConst = balanceCon
    #Checks to see if we have a positive balance constant for our tuple of weight initializations
        if balanceCheck(x,y,WI,3) > maxConst:
    #Set alpha so that alpha*balanceCheck is the tight bound for the balanced condition
            alpha = maxConst/balanceCheck(x,y,WI,3) 
            works = False
        iterin += 1

#Computes upper bound of stepsize according to Theorem 2.4
    step = stepsize(x,y,WI,3,alpha)

    Wlist = []
    for param in WIlist:
        Wlist.append(torch.tensor(param))


    W = np.matmul(np.matmul(Wlist[2], Wlist[1]), Wlist[0])
    dList = [5,2,2,5]
    model = NeuralNet2(3,dList,Wlist)
    step = 0.9*step
    x = torch.tensor(x).float()
    y = torch.tensor(y).float() 
    iterations = 5000
    time = list(range(iterations))
    figure(figsize=(8, 6), dpi=80)


    nextIter = True
    while nextIter:   
        opt = SGD(model.parameters(), lr = 0.9*step)
        L = nn.MSELoss(reduction = 'sum')

    
        lossList = []
    

        for epoch in range(iterations):
            yhat = model(x)
            loss = L(yhat, y)
        
    # backpropagation
            opt.zero_grad()
            loss.backward()
            opt.step()
            lossList.append(loss.item())
        step = step*2
# convergence to global minimizer
        if math.isnan(loss.item()):
            nextIter = False
            countList.append(step)

countsList = [round(item, 2) for item in countList]
plt.hist(x=countList, bins='auto', color='#0504aa')
plt.title('Fixed Step Size of Divergence')
plt.xlabel('Step Size')
plt.ylabel('Frequency')
plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

"""Numerical Experiments on Critical Points and Implicit Regularization"""

import numpy as np
import matplotlib.pyplot as plt
import random
import torch
from torch import nn
from torch.optim import SGD

class NeuralNet(nn.Module):
    
    def __init__(self, d1, d2, d3, d4):
        super(NeuralNet, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(d1, d2, bias = False),
            nn.Linear(d2, d3, bias = False),
            nn.Linear(d3, d4, bias = False)
        )
        
    def forward(self, x):
        return self.model(x)
    
x = np.random.normal(size = (1000,5))
beta = np.diag([5,4,3,2,1])
y = np.matmul(x,beta)

"""print(x.shape)
print(beta.shape)
print(y.shape)"""

x = torch.tensor(x).float()
y = torch.tensor(y).float() + torch.normal(0, 0.01, size = (1000,5))

# compute sigmas to find critical points
sigma_yx = np.matmul(y.T, x)
sigma_xx = np.matmul(x.T, x)
sigma_yy = np.matmul(y.T, y)
sigma_xy = np.matmul(x.T, y)
sigma_12 = np.matmul(np.matmul(sigma_yx, np.linalg.inv(sigma_xx)), x.T)
sigma = np.matmul(sigma_12, sigma_12.T)
U, D, V = np.linalg.svd(sigma_12)
U2, D2, V2 = np.linalg.svd(sigma) # need this for lambda_i

# print(D2)
temp = np.matmul(sigma_yx, np.linalg.inv(sigma_xx))

L = nn.MSELoss(reduction = 'sum')

# Critical points with r = rmax = 4
W1 = np.matmul(np.matmul(U[:,0:4],U[:,0:4].T),temp) # S = (1,2,3,4) = [[1, rmax]] --> global minimum
minLoss = L(np.matmul(x,W1.T),y)
# print(W1)
# print("Loss at this point:", minLoss) # this and the line below are the same, if Achour's formula is correct
# print("Loss at this critical point as predicted in Achour's paper:", np.trace(sigma_yy)-sum(D2[0:4]))

# Now let S = (1,2,3,4). This is a strict saddle point because r = rmax = 4 but S is not [[1, rmax]](theorem 1)
#W2 = np.matmul(np.matmul(U[:,[0,1,2,3]],U[:,[0,1,2,3]].T),temp) 
#critLoss1 = L(np.matmul(x,W2.T),y)

# Now let S = (1,2,3).
W3 = np.matmul(np.matmul(U[:,[0,1,2]],U[:,[0,1,2]].T),temp) 
critLoss2 = L(np.matmul(x,W3.T),y)

# Now let S = (1,2)
W4 = np.matmul(np.matmul(U[:,[0,1]],U[:,[0,1]].T),temp) 
critLoss3 = L(np.matmul(x,W4.T),y)

# Now let S = (1)
W5 = np.matmul(np.matmul(U[:,[0]],U[:,[0]].T),temp) 
critLoss4 = L(np.matmul(x,W5.T),y)

L = nn.MSELoss(reduction = 'sum')
# print(W2)
# print("Loss at this point:", critLoss1) # this and the line below are the same, if Achour's formula is correct
# print("Loss at this critical point as predicted in Achour's paper:", np.trace(sigma_yy)-sum(D2[[0,1,2,4]]))

model = NeuralNet(5,4,4,5) 
model = model.float()
opt = SGD(model.parameters(), lr = 10**(-6))
l3 = []
p1 = True # switch to false if you want to print weights when loss is near critical points loss
p2 = True # switch to false if you want to print weights when loss is near critical points loss
p3 = True # switch to false if you want to print weights when loss is near critical points loss
for epoch in range(3000):
    yhat = model(x)
    loss = L(yhat, y)
        
    # backpropagation
    opt.zero_grad()
    loss.backward()
    l3.append(loss.item())
    opt.step()
    if p1 == False:
      if (abs(loss.item() - critLoss2) <= 5):
        Wlist = []
        for param in model.parameters():
          Wlist.append(param.detach().numpy())
        print(np.matmul(np.matmul(Wlist[2], Wlist[1]), Wlist[0]))
        p1 = True

    if p2 == False:
      if (abs(loss.item() - critLoss3) <= 10):
        Wlist = []
        for param in model.parameters():
          Wlist.append(param.detach().numpy())
        print(np.matmul(np.matmul(Wlist[2], Wlist[1]), Wlist[0]))
        p2 = True
    
    if p3 == False:
      if (abs(loss.item() - critLoss4) <= 30):
        Wlist = []
        for param in model.parameters():
          Wlist.append(param.detach().numpy())
        print(np.matmul(np.matmul(Wlist[2], Wlist[1]), Wlist[0]))
        p3 = True

# convergence to global minimizer
print(f"Epoch:{epoch} loss is {loss.item()}")

Wlist = []
for param in model.parameters():
    Wlist.append(param.detach().numpy())

"""print(np.matmul(np.matmul(Wlist[2],Wlist[1]), Wlist[0]))
print(Wlist[2].shape)
print(Wlist[1].shape)
print(Wlist[0].shape)

W = np.matmul(np.matmul(Wlist[2], Wlist[1]), Wlist[0])
print(W.shape)
print(W)"""

xaxis = np.arange(3000)
plt.figure(figsize = (16,9))
plt.plot(xaxis, l3, label = "Loss history")
plt.axhline(y=minLoss, color='r', linestyle='-', label = "Loss at global minimum")
# plt.axhline(y=critLoss1, color='black', linestyle='-', label = "Loss at rank 4 min.")
plt.axhline(y=critLoss2, color='orange', linestyle='-', label = "Loss at rank 3 min.")
plt.axhline(y=critLoss3, color='brown', linestyle='-', label = "Loss at rank 2 min.")
plt.axhline(y=critLoss4, color='purple', linestyle='-', label = "Loss at rank 1 min.")
# plt.plot(x, l2, label = "init. at non strict saddle point")
# plt.plot(x, l2, label = "init. at non strict saddle point")
plt.xlabel("Epochs", fontsize = "x-large")
plt.ylabel("Loss", fontsize = "x-large")
plt.xticks(fontsize = "x-large")
plt.yticks(fontsize = "x-large")
plt.legend(fontsize = "x-large")
plt.title("Loss History", fontsize = "x-large")
e1 = torch.normal(0, 0.05, size = (4,5))
e2 = torch.normal(0, 0.05, size = (4,4))
e3 = torch.normal(0, 0.05, size = (5,4))

# Critical points with r = 3 < rmax = 4
# Now we will differentiate between saddle points in the case where r < rmax.
# Let's build a tightened and a non tightened critical point following the proof in appendix B.8
W_3 = np.hstack((U[:,[0,1,2]], np.zeros(shape = (5,1))))
W_21 = np.hstack((np.eye(3), np.zeros(shape = (3,1))))
W_2z = np.vstack((W_21, np.zeros(shape = (1,4)))) # for tightened critical point --> non strict saddle point
W_2i = np.eye(4) # for nontightened critical point --> strict saddle point
W_1 = np.vstack((np.matmul(U[:,[0,1,2]].T, temp), np.zeros(shape = (1,5))))

class NeuralNet2(nn.Module): # class to initialize network manually
    
    def __init__(self, N, dList, W = None):
        super(NeuralNet2, self).__init__()
        modules = []
        self.weights = []
        for i in range(N):
          modules.append(nn.Linear(dList[i-1], dList[i], bias = False))
          modules[i].weight.data = torch.nn.Parameter(W[i])
          self.weights.append(modules[i].weight.data)
        self.model = nn.Sequential(*modules)

    def forward(self,x):
        return self.model(x)

W_1 = torch.tensor(W_1) + e1
W_2 = torch.tensor(W_2i) + e2 # here change 2z into 2i or viceversa to get non strict saddle points ("worse") / strict ("better")
W_3 = torch.tensor(W_3) + e3
model2 = NeuralNet2(3, [5,4,4,5], [W_1, W_2, W_3])
# print(model2.weights)

model2 = model2.float()
opt = SGD(model2.parameters(), lr = 10**(-6))
l1 = []
for epoch in range(3000):
    yhat = model2(x)
    loss = L(yhat, y)
        
    # backpropagation
    opt.zero_grad()
    loss.backward()
    opt.step()
    l1.append(loss.item())
# convergence to global minimizer
print(f"Epoch:{epoch} loss is {loss.item()}")

W_1 = torch.tensor(W_1) + e1
W_2 = torch.tensor(W_2z) + e2 # here change 2z into 2i or viceversa to get non strict saddle points ("worse") / strict ("better")
W_3 = torch.tensor(W_3) + e3
model2 = NeuralNet2(3, [5,4,4,5], [W_1, W_2, W_3])
# print(model2.weights)

model2 = model2.float()
opt = SGD(model2.parameters(), lr = 10**(-6))
l2 = []
for epoch in range(3000):
    yhat = model2(x)
    loss = L(yhat, y)
        
    # backpropagation
    opt.zero_grad()
    loss.backward()
    opt.step()
    l2.append(loss.item())
# convergence to global minimizer
print(f"Epoch:{epoch} loss is {loss.item()}")
xaxis = np.arange(3000)
plt.figure(figsize = (16,9))
plt.plot(xaxis, l1, label = "init. at strict saddle point")
plt.plot(xaxis, l2, label = "init. at non strict saddle point")
plt.plot(xaxis, l3, label = "random init.")
plt.xlabel("Epochs", fontsize = "x-large")
plt.ylabel("Loss", fontsize = "x-large")
plt.xticks(fontsize = "x-large")
plt.yticks(fontsize = "x-large")
plt.legend(fontsize = "x-large")
plt.title("Loss for Different Initializations", fontsize = "x-large")
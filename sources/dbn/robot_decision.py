#!/usr/bin/env python
# coding: utf-8

# In[62]:


import pandas as pd
import numpy as  np
from pgmpy.factors.discrete import TabularCPD
from pgmpy.models import BayesianNetwork as BN
from pgmpy.models import DynamicBayesianNetwork as DBN
from pgmpy.inference import DBNInference, VariableElimination
import glob
import sys


# In[2]:


bnet = BN()
bnet.add_edges_from([
    ('start_close', 'start_action'),
    ('next_close', 'next_action'), 
    ('next_action', 'next_door'),
    ('start_close', 'next_action'),
    ('start_action', 'next_door')
])


# In[3]:


#Close to door or not. If dist < sensor_dist then 0.9 prob it is close
close_cpd = TabularCPD('start_close', 2, [[0.1], [0.9]])

#Probability a certain action is taken. For first step, if Close is True, 0 prob it walks back, 0.15 it walks forward, 0.85 it stays
action_cpd = TabularCPD('start_action', 3, [[0, 0], 
                                   [0.89, 0.15], 
                                   [0.11, 0.85]],
                    evidence=['start_close'],
                    evidence_card=[2])

c_i_cpd = TabularCPD('next_close', 2, [[0.1],
                                   [0.9]])

a_i_cpd = TabularCPD('next_action', 3, [[0, 0.12, 0, 0.10], 
                                   [0.8, 0, 0.92, 0], 
                                   [0.2, 0.88, 0.08, 0.9]],
                    evidence=['start_close', 'next_close'],
                    evidence_card=[2, 2])

p_i_cpd = TabularCPD('next_door', 2, [[0.9, 0.95, 0.97, 0.3, 0.98, 0.98, 0.02, 0.95, 0.98], 
                                   [0.1, 0.05, 0.03, 0.7, 0.02, 0.02, 0.98, 0.05, 0.03]],
                    evidence=['start_action', 'next_action'],
                    evidence_card=[3, 3])


# In[4]:


bnet.add_cpds(close_cpd, action_cpd, c_i_cpd, a_i_cpd, p_i_cpd)


# In[5]:


bnet.check_model()


# In[6]:


bnet.nodes()


# In[7]:


bnet.edges()


# In[8]:


bnet.get_independencies()


# In[9]:


from pgmpy.inference import VariableElimination

infer = VariableElimination(bnet)
probs = infer.query(['next_action'], evidence={'start_close':0, 'next_close':1})
print(probs)


# In[17]:


def queryModel(inf, qry: str, prev: int, curr: int):
    
    if qry == 'a':
        probs = inf.query(['next_action'], {'start_close':prev, 'next_close':curr})
        return np.random.choice(3, p=probs.values)
    elif qry == 'd':
        probs = inf.query(['next_door'], {'start_action':prev, 'next_action':curr})
        return np.random.choice(2, p=probs.values)
    
    return -1


# In[61]:


decision = queryModel(infer, str(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))

print(decision)


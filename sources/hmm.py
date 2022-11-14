import numpy as np
import matplotlib.pyplot as plt
from hmmlearn import hmm
np.set_printoptions(formatter={'float_kind':'{:f}'.format})
model = hmm.MultinomialHMM(n_components=2,  n_iter=1)
model.startprob_ = np.array([0.7, 0.3])
model.n_features = 3
model.transmat_ = np.array([[0.9940766550522648, 0.005923344947735192],[0.017857142857142856, 0.9821428571428571],
 ])

vocabulary = ["b", "s", "f"]
emission_probs = np.array([[0.1137, 0.5937, 0.0434],[0.0023, 0.0277, 0.2183],
                           ])
model.emissionprob_=emission_probs

np_arr = np.array([[0],[1],[2],[2],[2],[2],[1],[1],[1],[1],[2],[2],[2],[2],[2],[2],[2],[2],[2],[0],[0],[0]])
#print(np_arr[:, None])
print(model.score_samples(np_arr))
#print(np_arr[:, None])
#model.score_samples(np_arr)
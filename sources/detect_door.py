import pandas as pd
import numpy as  np
from pgmpy.factors.discrete import TabularCPD
from pgmpy.models import DynamicBayesianNetwork as DBN
from pgmpy.inference import DBNInference, VariableElimination

class DoorDetector:
    '''
        Class to detect door using the sonar data and the DBN model
    '''

    # TODO: verify the model structure is built correctly
    def __init__(self, data_path):
        '''
            Initialize the DoorDetector class
            input: data_path - path to the data (cpt value csvs)
        '''
        # door model
        self.dbnet = DBN()

        # add nodes
        self.dbnet.add_edges_from([
            (('C', 0), ('A', 0)),
            (('A', 0), ('P', 0)),
            (('C', 1), ('A', 1)),
            (('A', 1), ('P', 1)),
            (('C', 0), ('A', 1)),
            (('A', 0), ('P', 1)),
        ])

        # add cpds
        # c_start_cpd = TabularCPD(('C', 0), 2, [[0.5], [0.5]])

        # a_i_cpd = TabularCPD(('A', 0), 3, [[0.3, 0.85],
        #                                 [0.3, 0.1],
        #                                 [0.4, 0.05]],
        #                     evidence=[('C', 0)],
        #                     evidence_card=[2])

        # p_i_cpd = TabularCPD(('P', 0), 2, [[0.2, 0.3, 0.4],
        #                                 [0.8, 0.7, 0.6]],
        #                     evidence=[('A', 0)],
        #                     evidence_card=[3])

        # c_trans_cpd = TabularCPD(('C', 1), 2, [[0.4], [0.6]])

        # a_trans_cpd = TabularCPD(('A', 1), 3, [[0.3, 0.85, 0.34 ,0.66],
        #                                 [0.3, 0.1, 0.21, 0.23],
        #                                 [0.4, 0.05, 0.45, 0.11]],
        #                     evidence=[('C', 0), ('C', 1)],
        #                     evidence_card=[2, 2])

        # p_trans_cpd = TabularCPD(('P', 1), 2, [[0.2, 0.3, 0.4, 0.2, 0.3, 0.4, 0.2, 0.3, 0.4],
        #                                 [0.8, 0.7, 0.6, 0.8, 0.7, 0.6, 0.8, 0.7, 0.6]],
        #                     evidence=[('A', 0), ('A', 1)],
        #                     evidence_card=[3, 3])

        params = self.process_cpts(data_path)
        # params = (c_start_cpd, a_i_cpd, p_i_cpd, c_trans_cpd, a_trans_cpd, p_trans_cpd)

        self.dbnet.add_cpds(*params)

        self.dbnet.initialize_initial_state()

        self.dbn_inf = DBNInference(self.dbnet)

        self.timestep = 0

        # dbnet.check_model()

    # TODO: adjust for out needs
    def detect_door(self, timestep, evidence):
        '''
            Detect the door using the sonar data, and the robot
            actions as evidence and the DBN model
        '''
        # update the timestep
        self.timestep = timestep

        # evidence = {('A', 1):0, ('P', 1):1}
        res = self.dbn_inf.query([('P', timestep)], evidence)[('P', timestep)].values
        print(res)
        # process the res for output
        return res
        

    # TODO: implement to read the cpt values from the csvs into the DBN model
    def process_cpts(self, data_path):
        '''
            Process the cpt values from the csv files into the DBN
            input: data_path - path to the data (cpt value csvs)
        '''
        # cpt_files = glob.glob(data_path + '/*.csv')
        # cpt_files.sort()
        # cpt_values = []
        # for cpt_file in cpt_files:
        #     cpt_values.append(pd.read_csv(cpt_file, header=None).values)

        # return tuple of tabular cpds
        return
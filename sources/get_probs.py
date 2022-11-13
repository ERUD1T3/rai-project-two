# get probabilities of the sonar readings
import csv

# read the data from the csv file
def read_from_csv(path, n_samples=150):
    time_arr = []
    x_array = []
    z_array = []
    a_array = []
    d_array = []
    time_counter = 0
    threshold_with_offset = 0.3
    with open(path, 'r') as csvfile:
        plots = csv.reader(csvfile, delimiter=',')
        # skip the first line
        next(plots)
        # read the data and stop at n_samples
        for row in plots:
            # print(row)
            # get the time
            time_arr.append(time_counter)
            time_counter += 1
            # parse the row from list string to tuple
            x = row[1].strip('[]').split(',')
            x_array.append((float(x[0]), float(x[1])))
            # get the sonar readings
            z = float(row[2]) < threshold_with_offset
            z_array.append(z)
            # get the action
            a = None
            if row[3] == 'backward':
                a = 0
            elif row[3] == 'forward':
                a = 1
            else: # stay 
                a = 2
            a_array.append(a)
            # get the door reading
            d_array.append(row[4] == 'True')

            # check if we have read enough samples
            # if len(time_arr) >= n_samples:
            #     break

    return time_arr, x_array, z_array, a_array, d_array

# compute probability
def compute_prob(array, cardinality=2):
    # computer probabilities based on count
    # get the number of times true appears in the array
    if len(array) == 0: 
        if cardinality == 2:
            return 0.5, 0.5
        elif cardinality == 3:
            return 0.33, 0.33, 0.33
        else:
            return None

    if cardinality == 2:
        count = 0.0
        for x in array:
            if x: count += 1
        return 1 - count/len(array), count/len(array)

    if cardinality == 3:
        count = [0.0, 0.0, 0.0]
        for x in array:
            count[x] += 1
        return count[0]/len(array), count[1]/len(array), count[2]/len(array)

# generate cpts based on samples
def generate_cpts(samples):
    # generate cpts based on samples
    # sample is 3D array
    # first dimension is the number of samples
    # second dimension is the number of time steps
    # third dimension is the number of variables
    # return cpts based on trues

    # get the number of samples
    num_samples = len(samples)
    print("number of samples: {}".format( num_samples))
    # get the number of time steps
    # num_time_steps = len(samples[0][0])
    # print("number of time steps: {}".format(num_time_steps))
    # get the number of variables
    num_vars = len(samples[0])
    print("number of variables: {}".format( num_vars))
    # number of time steps 
    num_time_steps = 170

    # find probabilities for each variable at the given time step
    z_cpts = {}
    a_cpts = {}
    d_cpts = {}

    # print the samples
    print(samples)

    # for first timestep
    # z_cpts['z0'] = compute_prob([x[0] for x in samples[0]])

    # get z cpts
    # for each time step
    for t in range(num_time_steps):
        # for each variable skip the first one
        var = 2 # z
        # get the array of values for the variable at the given time step
        array = []
        for sample in samples:
            # add the value of the variable at the given time step
            try:
                array.append(sample[var][t])
            except:
                continue

            
        # get the probabilities of the sonar readings based on the check function
        print(array)
        if len(array) == 0: break # break if there are no samples at this time step
        # computer probabilities based on count
        false_p, true_p = compute_prob(array, cardinality=2)
        # add the probability to the cpts
        z_cpts[f'z{t}'] = (false_p, true_p)
        # print cpt with 3 decimal places
        # print("cpt[('z', {})] = {:.3f}".format(t, prob))
            
    # get a cpts depending on z
    # for each time step  
    for t in range(num_time_steps):
        # for the first timestep
        if t == 0:
            # for each variable skip the first one
            var = 3 # a
            # get the array of values for the variable at the given time step
            z_true_array = []
            z_false_array = []
            for sample in samples:
                # count the number of times the sonar reading is true
                if sample[2][t]:
                    z_true_array.append(sample[var][t])
                else:
                    z_false_array.append(sample[var][t])
        
            # get the probabilities 
            a0_ztrue, a1_ztrue, a2_ztrue = compute_prob(z_true_array, cardinality=3)
            a0_zfalse, a1_zfalse, a3_zfalse = compute_prob(z_false_array, cardinality=3)
            # add the probability to the cpts
            a_cpts[f'a{t}|z{t}=True'] = (a0_ztrue, a1_ztrue, a2_ztrue)
            a_cpts[f'a{t}|z{t}=False'] = (a0_zfalse, a1_zfalse, a3_zfalse)
        else:
            # for each variable skip the first one
            var = 3
            # get the array of values for the variable at the given time step
            zt_true_ztm1_true_array = []
            zt_true_ztm1_false_array = []
            zt_false_ztm1_true_array = []
            zt_false_ztm1_false_array = []
            for sample in samples:
                try:
                    # count the number of times the sonar reading is true
                    if sample[2][t] and sample[2][t-1]:
                        zt_true_ztm1_true_array.append(sample[var][t])
                    elif sample[2][t] and not sample[2][t-1]:
                        zt_true_ztm1_false_array.append(sample[var][t])
                    elif not sample[2][t] and sample[2][t-1]:
                        zt_false_ztm1_true_array.append(sample[var][t])
                    else:
                        zt_false_ztm1_false_array.append(sample[var][t])
                except:
                    continue

            # get the probabilities
            if len(zt_true_ztm1_true_array) == 0 and \
                len(zt_true_ztm1_false_array) == 0 and \
                len(zt_false_ztm1_true_array) == 0 and \
                len(zt_false_ztm1_false_array) == 0:
                break

            a0_zttrue_ztm1true, a1_zttrue_ztm1true, a2_zttrue_ztm1true = compute_prob(
                zt_true_ztm1_true_array, cardinality=3)
            a0_zttrue_ztm1false, a1_zttrue_ztm1false, a2_zttrue_ztm1false = compute_prob(
                zt_true_ztm1_false_array, cardinality=3)
            a0_ztfalse_ztm1true, a1_ztfalse_ztm1true, a2_ztfalse_ztm1true = compute_prob(
                zt_false_ztm1_true_array, cardinality=3)
            a0_ztfalse_ztm1false, a1_ztfalse_ztm1false, a2_ztfalse_ztm1false = compute_prob(
                zt_false_ztm1_false_array, cardinality=3)

            # add the probability to the cpts
            a_cpts[f'a{t}|z{t}=True,z{t-1}=True'] = (a0_zttrue_ztm1true, a1_zttrue_ztm1true, a2_zttrue_ztm1true)
            a_cpts[f'a{t}|z{t}=True,z{t-1}=False'] = (a0_zttrue_ztm1false, a1_zttrue_ztm1false, a2_zttrue_ztm1false)
            a_cpts[f'a{t}|z{t}=False,z{t-1}=True'] = (a0_ztfalse_ztm1true, a1_ztfalse_ztm1true, a2_ztfalse_ztm1true)
            a_cpts[f'a{t}|z{t}=False,z{t-1}=False'] = (a0_ztfalse_ztm1false, a1_ztfalse_ztm1false, a2_ztfalse_ztm1false)



    # get d cpts depending on a
    # for each time step
    for t in range(num_time_steps):
        # for the first timestep
        if t == 0:
            # for each variable skip the first one
            var = 4
            # get the array of values for the variable at the given time step
            a_0_array = []
            a_1_array = []
            a_2_array = []
            for sample in samples:
                # count the number of times the sonar reading is true
                if sample[3][t] == 0:
                    a_0_array.append(sample[var][t])
                elif sample[3][t] == 1:
                    a_1_array.append(sample[var][t])
                else:
                    a_2_array.append(sample[var][t])

            # get the probabilities 
            not_prob_0, prob_0 = compute_prob(a_0_array, cardinality=2)
            not_prob_1, prob_1 = compute_prob(a_1_array, cardinality=2)
            not_prob_2, prob_2 = compute_prob(a_2_array, cardinality=2)
            # add the probability to the cpts
            d_cpts[f'd{t}|a{t}=0'] = (not_prob_0, prob_0)
            d_cpts[f'd{t}|a{t}=1'] = (not_prob_1, prob_1)
            d_cpts[f'd{t}|a{t}=2'] = (not_prob_2, prob_2)
        else:
            # for each variable skip the first one
            var = 4
            # get the array of values for the variable at the given time step
            at_0_atm1_0_array = []
            at_0_atm1_1_array = []
            at_0_atm1_2_array = []
            at_1_atm1_0_array = []
            at_1_atm1_1_array = []
            at_1_atm1_2_array = []
            at_2_atm1_0_array = []
            at_2_atm1_1_array = []
            at_2_atm1_2_array = []

            for sample in samples:
                # count the number of times the sonar reading is true
                try:
                    if sample[3][t] == 0:
                        if sample[3][t-1] == 0:
                            at_0_atm1_0_array.append(sample[var][t])
                        elif sample[3][t-1] == 1:
                            at_0_atm1_1_array.append(sample[var][t])
                        else:
                            at_0_atm1_2_array.append(sample[var][t])
                    elif sample[3][t] == 1:
                        if sample[3][t-1] == 0:
                            at_1_atm1_0_array.append(sample[var][t])
                        elif sample[3][t-1] == 1:
                            at_1_atm1_1_array.append(sample[var][t])
                        else:
                            at_1_atm1_2_array.append(sample[var][t])
                    else:
                        if sample[3][t-1] == 0:
                            at_2_atm1_0_array.append(sample[var][t])
                        elif sample[3][t-1] == 1:
                            at_2_atm1_1_array.append(sample[var][t])
                        else:
                            at_2_atm1_2_array.append(sample[var][t])
                except:
                    continue

            # get the probabilities
            if len(at_0_atm1_0_array) == 0 and \
                len(at_0_atm1_1_array) == 0 and \
                len(at_0_atm1_2_array) == 0 and \
                len(at_1_atm1_0_array) == 0 and \
                len(at_1_atm1_1_array) == 0 and \
                len(at_1_atm1_2_array) == 0 and \
                len(at_2_atm1_0_array) == 0 and \
                len(at_2_atm1_1_array) == 0 and \
                len(at_2_atm1_2_array) == 0:
                break

            not_prob_0_0, prob_0_0 = compute_prob(at_0_atm1_0_array, cardinality=2)
            not_prob_0_1, prob_0_1 = compute_prob(at_0_atm1_1_array, cardinality=2)
            not_prob_0_2, prob_0_2 = compute_prob(at_0_atm1_2_array, cardinality=2)
            not_prob_1_0, prob_1_0 = compute_prob(at_1_atm1_0_array, cardinality=2)
            not_prob_1_1, prob_1_1 = compute_prob(at_1_atm1_1_array, cardinality=2)
            not_prob_1_2, prob_1_2 = compute_prob(at_1_atm1_2_array, cardinality=2)
            not_prob_2_0, prob_2_0 = compute_prob(at_2_atm1_0_array, cardinality=2)
            not_prob_2_1, prob_2_1 = compute_prob(at_2_atm1_1_array, cardinality=2)
            not_prob_2_2, prob_2_2 = compute_prob(at_2_atm1_2_array, cardinality=2)
            # add the probability to the cpts
            d_cpts[f'd{t}|a{t}=0,a{t-1}=0'] = (not_prob_0_0, prob_0_0)
            d_cpts[f'd{t}|a{t}=0,a{t-1}=1'] = (not_prob_0_1, prob_0_1)
            d_cpts[f'd{t}|a{t}=0,a{t-1}=2'] = (not_prob_0_2, prob_0_2)
            d_cpts[f'd{t}|a{t}=1,a{t-1}=0'] = (not_prob_1_0, prob_1_0)
            d_cpts[f'd{t}|a{t}=1,a{t-1}=1'] = (not_prob_1_1, prob_1_1)
            d_cpts[f'd{t}|a{t}=1,a{t-1}=2'] = (not_prob_1_2, prob_1_2)
            d_cpts[f'd{t}|a{t}=2,a{t-1}=0'] = (not_prob_2_0, prob_2_0)
            d_cpts[f'd{t}|a{t}=2,a{t-1}=1'] = (not_prob_2_1, prob_2_1)
            d_cpts[f'd{t}|a{t}=2,a{t-1}=2'] = (not_prob_2_2, prob_2_2)
    

    return z_cpts, a_cpts, d_cpts


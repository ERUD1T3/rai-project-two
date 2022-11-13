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
    if len(array) == 0: return 0
    count = 0.0
    for x in array:
        if x: count += 1
    return count/len(x_array)

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
    num_time_steps = len(samples[0][0])
    print("number of time steps: {}".format( num_time_steps))
    # get the number of variables
    num_vars = len(samples[0])
    print("number of variables: {}".format( num_vars))

    # find probabilities for each variable at the given time step
    z_cpts = {}
    a_cpts = {}
    d_cpts = {}

    # print the samples
    print(samples)

    # get z cpts
    # for each time step
    for t in range(num_time_steps):
        # for each variable skip the first one
        var = 1
        # get the array of values for the variable at the given time step
        x_array = []
        for sample in samples:
            # print length of sample
            # print(len(sample))
            # print(len(sample[0]))
            # print var and t
            # print("var: {}".format( var))
            # print("t: {}".format( t))
            # print sample at var and t
            # print("sample at {}{} =  {}".format(var, t, sample[var][t]))
            x_array.append(sample[var][t])
        # get the probabilities of the sonar readings based on the check function
        bools = x_array
        print(bools)
        # computer probabilities based on count
        prob = compute_prob(bools)
        # add the probability to the cpts
        
        z_cpts[f'z_{t}'] = prob
        # print cpt with 3 decimal places
        # print("cpt[('z', {})] = {:.3f}".format(t, prob))
            
    # get a cpts depending on z
    # for each time step  
    for t in range(num_time_steps):
        # for each variable skip the first one
        var = 2
        # get the array of values for the variable at the given time step
        z_true_array = []
        z_false_array = []
        for sample in samples:
            # count the number of times the sonar reading is true
            if sample[1][t]:
                z_true_array.append(sample[var][t])
            else:
                z_false_array.append(sample[var][t])
    
        # get the probabilities for the sonar readings true and false
        prob_true = compute_prob(z_true_array)
        prob_false = compute_prob(z_false_array)
        # add the probability to the cpts
        a_cpts[f'a_{t}|z=True'] = prob_true
        a_cpts[f'a_{t}|z=False'] = prob_false

    # get d cpts depending on a
    # for each time step
    for t in range(num_time_steps):
        var = 3
        # get the array of values for the variable at the given time step
        a_true_array = []
        a_false_array = []
        for sample in samples:
            # count the number of times the sonar reading is true
            if sample[2][t]:
                a_true_array.append(sample[var][t])
            else:
                a_false_array.append(sample[var][t])

        # get the probabilities for the sonar readings true and false
        prob_true = compute_prob(a_true_array)
        prob_false = compute_prob(a_false_array)
        # add the probability to the cpts
        d_cpts[f'd_{t}|a=True'] = prob_true
        d_cpts[f'd_{t}|a=False'] = prob_false

    

    return z_cpts, a_cpts, d_cpts


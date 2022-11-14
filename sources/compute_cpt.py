# read samples and compute probabilities
from get_probs import read_from_csv, generate_cpts
import os

def main():
    path = '../data/samples/'
    # read all files in the directory
    try:
        files = os.listdir(path)
    except:
        print("Could not find directory, try to navigate to sources/ before running this script")
        return
    print(files)
    # read the data from the csv file
    samples = []
    for file in files:
        # read the data
        time_arr, x_array, z_array, a_array, d_array = read_from_csv(path + file)
        # append the data to the samples
        samples.append([time_arr, x_array, z_array, a_array, d_array])
    
    print(len(samples)) # number of samples
    print(len(samples[0])) # number of variables
    print(len(samples[0][0])) # number of time steps
    print(samples[0][1][0]) #

    # generate cpts
    z_cpts, a_cpts, d_cpts = generate_cpts(samples)

    # average across all timesteps
    avg_z_cpts = {}
    avg_a_cpts = {}
    avg_d_cpts = {}

    avg_z_cpts['z0'] = z_cpts['z0']
    # for all the keys in the z_cpts skip the first one
    false = 0.0
    true = 0.0

    for key in z_cpts.keys():
        if key == 'z0':
            continue
        false += z_cpts[key][0]
        true += z_cpts[key][1]
        
    avg_z_cpts['z1'] = (false/(len(z_cpts) - 1), true/len(z_cpts))

    # print the cpts
    print("z_cpts: {}".format(z_cpts))
    print("a_cpts: {}".format(a_cpts))
    print("d_cpts: {}".format(d_cpts))

    # write the z_cpts to a file
    with open('../data/cpts/z_cpts.txt', 'w') as f:
        # write the cpts key and values
        for cpt in z_cpts:
            f.write("{}: {}\n".format(cpt, z_cpts[cpt]))

    # write the a_cpts to a file
    with open('../data/cpts/a_cpts.txt', 'w') as f:
        # write the lines and their probabilities
        for cpt in a_cpts:
            f.write("{}: {}\n".format(cpt, a_cpts[cpt]))

    # write the d_cpts to a file
    with open('../data/cpts/d_cpts.txt', 'w') as f:
        # write the lines and their probabilities
        for cpt in d_cpts:
            f.write("{}: {}\n".format(cpt, d_cpts[cpt]))

        

if __name__ == '__main__':
    main()
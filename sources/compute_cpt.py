# read samples and compute probabilities
from get_probs import read_from_csv, generate_cpts
import os

def main():

    # read all files in the directory
    try:
        files = os.listdir('../../data/samples/')
    except:
        print("Could not find directory, try to navigate to sources/test_files before running this script")
        return
    print(files)
    # read the data from the csv file
    samples = []
    for file in files:
        # read the data
        time_arr, z_array, a_array, d_array = read_from_csv('../../data/samples/' + file)
        # append the data to the samples
        samples.append([time_arr, z_array, a_array, d_array])
    
    print(len(samples))
    print(len(samples[0]))
    print(len(samples[0][0]))
    print(samples[0][0][0])

    # generate cpts
    z_cpts, a_cpts, d_cpts = generate_cpts(samples)

    # print the cpts
    print("z_cpts: {}".format(z_cpts))
    print("a_cpts: {}".format(a_cpts))
    print("d_cpts: {}".format(d_cpts))

    # write the z_cpts to a file
    with open('../../data/cpts/z_cpts.txt', 'w') as f:
        # write the cpts key and values
        for cpt in z_cpts:
            f.write("{}: {}\n".format(cpt, z_cpts[cpt]))

    # write the a_cpts to a file
    with open('../../data/cpts/a_cpts.txt', 'w') as f:
        # write the lines and their probabilities
        for cpt in a_cpts:
            f.write("{}: {}\n".format(cpt, a_cpts[cpt]))

    # write the d_cpts to a file
    with open('../../data/cpts/d_cpts.txt', 'w') as f:
        # write the lines and their probabilities
        for cpt in d_cpts:
            f.write("{}: {}\n".format(cpt, d_cpts[cpt]))

        

if __name__ == '__main__':
    main()
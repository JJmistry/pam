from python_module3_marker import solveGame
from scipy import special
import pickle as pkl
import math
from tqdm import tqdm
import os
import glob
import multiprocessing as mp
import random
import csv
from copy import deepcopy

def getStatistics(no_trials):
    """
    This models the probability of success as a binomial distribution (for more information about how a binomial distribution is modelled see the calculateBinomialProbability function. It is well known that a binomial distribution has
    mean,
        mu = N * Pi
    and standard deviation,
        sigma = sqrt( N * Pi * (1 - Pi) )
    where N is the number of trails and Pi is the probability that our program will win the game.

    This is used to calculate the mean and the the upper and lower bounds of the 99 confidence interval (i.e. 3 standard deviations). FYI N := no_trials and Pi := T_prob.

    Args:
        no_trials (int): This is the number of times a student's script was tested.

    Returns:
        A dictionary with the following keys. T_prob (float): is our estimate of the probability that our program correctly guesses a word when a word is randomly picked from our word list using a uniform distribution. no_trials (int): is the parameter passed to the function by the user. mu (float) is the mean acording to a binomial distrbution with probability of success as T_prob and the number of trials as no_trials. 3_sigma (float): is three standard deviations (i.e. ~99% confidence). u_bound (float): is the upper bound of the 99% confidence interval. l_bound (float): is the lower bound of the 99% confidence interval.

    Raises:
        None.
    """

    T_prop = 0.764 # Our estimate of the probability that our program will win a game
    mu = no_trials * T_prop # ~76.4 mean
    sigma3 = 3 * math.sqrt(no_trials * T_prop * (1 - T_prop)) # three standard deviations

    u_bound = mu + sigma3 # upper bound 99% CI
    l_bound = mu - sigma3 # lower bound 99% CI

    return {'T_prob': T_prop, 'no_trials': no_trials, 'mu': mu, '3_sigma': sigma3, 'u_bound': u_bound, 'l_bound': l_bound}

def calculateBinomialProbability(no_successes, no_trials, prob_success):
    """
    This models our algorithm's chance of winning a game as a binomial random variable and thus the probability of our algorithm winning x games in N trials is
    P(x) = N choose x * Pi^x * ( 1 - Pi^(N - x) )
    where N is the number of trials, x is the number of successes, and Pi is the probability of winning the game.

    Args:
	no_successes (int): The number of successes.
	no_trials (int): The number of trials.
	prob_success (float): The probability of winning a game.

    Returns (float):
	The probability of no_successes successes in no_trials number of trials.

    Raises:
	None.
    """

    no_combs = special.comb(no_trials, no_successes, exact = True)
    return no_combs * (prob_success ** no_successes) * (1 - prob_success) ** (no_trials - no_successes)

def listOfFilesToTest(list_of_python_files, no_repetitions, no_cores = None):
    """
    This function plays multiple games of a list of Python hangman games in parallel and returns the results.

    Args:
	list_of_python_files (list (str)): A list of hangman games to play where each string is a path to the Python file.
	no_repetitions (int): Number of times each hangman game is played.
	no_cores (None or int): Each hangman game can be played in parallel. no_cores gives the number of processes that can be spawned at one time. The default of None means use all available cores or is an integer that specifies how many processes to spawn simultaneously.

    Returns:
	A list of objects returned by the repeatSolver function for each of the hangman games to test.

    Raises:
	None.
    """

    # how many CPU cores to use (default is all available cores anything else needs to be passed by the user)
    if no_cores == None:
        pool = mp.Pool() # use all available cores
    else:
        pool = mp.Pool(processes = no_cores) # use no_cores number of cores

    results = pool.starmap(repeatSolver, zip(list_of_python_files, [no_repetitions] * len(list_of_python_files))) # play the game no_repetitions number of times for each of the python files (each file is tested in parallel

    return results

def repeatSolver(file_name, no_repetitions):
    """
    This this plays a student's hangman game multiple times using the solveGame function.

    Args:
	file_name (str): The path to the student's hangman script that needs to be solved.
	no_repetitions (int): The number of times that we should play the game.

    Returns (list):
	A list of objects returned by the solveGame function.

    Raises:
	None.
    """

    all_words = ['rarely', 'universe', 'notice', 'sugar', 'interference', 'constitution', 'we', 'minus', 'breath', 'clarify', 'take', 'recording', 'amendment', 'hut', 'tip', 'logical', 'cast', 'title', 'brief', 'none', 'relative', 'recently', 'detail', 'port', 'such', 'complex', 'bath', 'soul', 'holder', 'pleasant', 'buy', 'federal', 'lay', 'currently', 'saint', 'for', 'simple', 'deliberately', 'means', 'peace', 'prove', 'sexual', 'chief', 'department', 'bear', 'injection', 'off', 'son', 'reflect', 'fast', 'ago', 'education', 'prison', 'birthday', 'variation', 'exactly', 'expect', 'engine', 'difficulty', 'apply', 'hero', 'contemporary', 'that', 'surprised', 'fear', 'convert', 'daily', 'yours', 'pace', 'shot', 'income', 'democracy', 'albeit', 'genuinely', 'commit', 'caution', 'try', 'membership', 'elderly', 'enjoy', 'pet', 'detective', 'powerful', 'argue', 'escape', 'timetable', 'proceeding', 'sector', 'cattle', 'dissolve', 'suddenly', 'teach', 'spring', 'negotiation', 'solid', 'seek', 'enough', 'surface', 'small', 'search'] # a list of all possible words from word_list.txt
    results = [] 
    print('Testing file', file_name) # because this can take a long time these print outs let the user know how things are progressing
    for _ in range(no_repetitions):
        results.append(solveGame(file_name)) # apply solveGame to file_name no_repetitions number of times
    print('File', file_name, 'tested.') # because this can take a long time these print outs let the user know how things are progressing
    return results

if __name__ == "__main__":
    # running this script will test all the python scripts in the current directory 100 times and make suggestions of if the student should pass or faiil
    no_of_repetitions = 20
    file_list = []
    file_list = glob.glob('*.py') # get all .py files in the current directory

    stats = getStatistics(no_of_repetitions) # get the upper and lower bound of the 99% confidence interval
    file_list = list(set(file_list) - {'analyse_multiple_files.py', 'python_module3_marker.py'}) # these are .py files in the current directory that don't need to be tested
    results = listOfFilesToTest(file_list, no_of_repetitions) # test all the .py files in the current directory
    with open('results.pkl', 'wb') as f:
        pkl.dump(results, f) # save all the results as a pickle file so that users can see what happened in more detail if strange behaviour occurs

    ### PERFORM ANALYSIS
    summaries = [] # sumarise each 100 game test
    result_counts = {'wins': 0, 'losses': 0, 'errors': []} # this will be used to count how many wins losses and errors occured for each file
    # loop through all the results and count wins, losses, and errors for each file
    for idx1 in range(len(results)): # each file
        tmp_counts = deepcopy(result_counts)
        for idx2 in range(len(results[idx1])): # each of the 100 games per file
            if results[idx1][idx2][0] == True:
                tmp_counts['wins'] += 1
            elif results[idx1][idx2][0] == False:
                tmp_counts['losses'] += 1
            else: 
                tmp_counts['errors'] += [results[idx1][idx2][0]]

        if len(tmp_counts['errors']) > 0: #for each file see if there were any errors
            summaries.append((file_list[idx1], tmp_counts['wins'], tmp_counts['losses'], tmp_counts['errors'], 'error', 'NaN')) # if there are errors then we can't fully test the hangman game so the last two columns are 'error' and 'NaN'.
        elif tmp_counts['wins'] > stats['l_bound'] and tmp_counts['wins'] < stats['u_bound']: # if the tests mean is within the 99% CI then it looks like the student's hangman works correctly so the last two columns are 'pass' and the probability that this result would occur according to the binomial distribution.
            summaries.append((file_list[idx1], tmp_counts['wins'], tmp_counts['losses'], tmp_counts['errors'], 'pass', calculateBinomialProbability(tmp_counts['wins'], no_of_repetitions, stats['T_prob'])))
        else: # otherwise the program functioned correctly but did not statistically perform as expected (i.e. mean not within the 99% CI) so the last two columns are 'fail' and the probability that this result would occur according to the binomial distribution (i.e. probability that the game is correct but failed by chance). 
            summaries.append((file_list[idx1], tmp_counts['wins'], tmp_counts['losses'], tmp_counts['errors'], 'fail', calculateBinomialProbability(tmp_counts['wins'], no_of_repetitions, stats['T_prob'])))


    with open('results.csv','w') as out: # save the results as a CSV file.
        csv_out=csv.writer(out, delimiter = ';')
        csv_out.writerow(['file name', 'No. wins', 'No. losses', 'List of errors', 'Result', 'Probability that this result occurred by chance not error']) # column headers
        for row in summaries:
            csv_out.writerow(row)

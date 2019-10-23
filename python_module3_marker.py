import pexpect
import random
import tqdm
import multiprocessing as mp
import pandas as pd
import pickle as pkl

# this is a list of the words that the students need to read from the word_list.txt file
all_words = ['rarely', 'universe', 'notice', 'sugar', 'interference', 'constitution', 'we', 'minus', 'breath', 'clarify', 'take', 'recording', 'amendment', 'hut', 'tip', 'logical', 'cast', 'title', 'brief', 'none', 'relative', 'recently', 'detail', 'port', 'such', 'complex', 'bath', 'soul', 'holder', 'pleasant', 'buy', 'federal', 'lay', 'currently', 'saint', 'for', 'simple', 'deliberately', 'means', 'peace', 'prove', 'sexual', 'chief', 'department', 'bear', 'injection', 'off', 'son', 'reflect', 'fast', 'ago', 'education', 'prison', 'birthday', 'variation', 'exactly', 'expect', 'engine', 'difficulty', 'apply', 'hero', 'contemporary', 'that', 'surprised', 'fear', 'convert', 'daily', 'yours', 'pace', 'shot', 'income', 'democracy', 'albeit', 'genuinely', 'commit', 'caution', 'try', 'membership', 'elderly', 'enjoy', 'pet', 'detective', 'powerful', 'argue', 'escape', 'timetable', 'proceeding', 'sector', 'cattle', 'dissolve', 'suddenly', 'teach', 'spring', 'negotiation', 'solid', 'seek', 'enough', 'surface', 'small', 'search']

def solveGame(file_path):
    """
    This method tests student's hangman scripts according to the structure of the third module 'Python' instructions. It automatically plays the game to detect that it works correctly.

    Args:
        file_path (str): A string of a path to the student's hangman script.

    Returns:
        (return result (bool or str), hist (dict)) (tup): result is either True (bool), False (bool), or an error code (str). This means that our program won the game, lost the game, or was unable to finish the game because of some error, respectively. hist contains details about what happened in the gamer. guess_hist (list(str)): the guesses made by this program. word_progress_hist (list(str)): how the astericked word progressed as guesses were made. remaining_words_hist (list(list(str))): the program starts with a list of all the possible words and eliminates words as guesses are made this is a history of the remaining words. letters_by_occurence_hist (list(dict)): is a list of dictionaries where each dictionary shows the letter frequencies of all the words in the remaining words list at the time of that guess.

    Raises:
        All errors should be dealt with try and exception statements so that an error string is returned instead of a Python Error being raised.

    The library 'pexpect' is used to communicate with the student's hangman game.

    Our strategy starts with a list of all possible words, removes all words that don't match the length of the word we need to guess. It then guesses each vowel until a correct guess is made. Any words that don't contain the vowel in that location are removed from the word list. Once one vowel is correctly guessed the program then calculates all the letter frequencies of all the remaining words and then guesses the one that occurs the most (that hasn't already been guessed). This strategy was shown to win the game roughly 71% of the time.

    """

    # Load neccessary variables
    hist = {'guess_hist': [], 'word_progress_hist': [], 'remaining_words_hist': [], 'letters_by_occurence_hist': []} # This will hold the progressing of the game
    all_letters = 'abcdefghijklmnopqrstuvwxyz'
    consonants = 'bcdfghjklmnpqrstvwxz'
    vowels = 'aeiouy' # aparently 'y' is a vowel! I did not know that!
    vowel_list = [vowel for vowel in vowels]
    # run the student's hangman script and catch an errors
    try:
        child = pexpect.spawn('python ' + file_path)
        child.timeout = 1 # set the timeout wait to one second
    except:
        child.close()
        return 'Spawn error', hist
    # Create a while loop that runs until the game is completed
    finished_flag = False # tells the while loop when to stop (i.e. when the game has finished)
    first_loop = True # Indicates if it is within the first loop
    while not finished_flag:
        # If written correctly the student's script will only ever stop to ask for the user to make a guess with the string 'Please enter your next guess: ' or because the game is finished. This tests for this.
        try: 
            child.expect(['Please enter your next guess: ', pexpect.EOF]) # look for the program to ask for a new guess or the end of the game
        except:
            child.close()
            return 'Expect error', hist # The program has stopped for a reason other than what was specified in the student's instructions

        # this program needs to know what the student's script did before and at the time if the stop (pexpect classes this as after the stop which doesn't make sense to me but explains the variable names below).
        try:
            bfr_txt = child.before.decode().strip().lower() # gets the before string, converts it from binary into a string then strips it and converts it into lowercase letters
            bfr_txt = " ".join(bfr_txt.split()) # removes any double spaces from the string
        except:
            child.close()
            return 'bfr decode error', hist # either the before string object was not in binary (which it should be if the program is built according to the instructions)
        try:
            afr_txt = child.after.decode().strip().lower() # gets the before string, converts it from binary into a string then strips it and converts it into lowercase letters
            afr_txt = " ".join(afr_txt.split()) # removes any double spaces from the string
        except:
            if child.after == pexpect.EOF: # it is OK to throw an error in the try above if it's because the game ended (i.e. returned EOF)
                afr_txt = child.after # EOF does not need decoding etc cause it is not a string
            else: # if the try above failed and afr_txt is not EOF file the program is not built according to instructions so return error code
                child.close()
                return 'afr decode error', hist
        if afr_txt == pexpect.EOF: # if game has ended test to see if the game was won, lost or if it ended in a unacceptable way
            if 'congratulations you win' in bfr_txt: # we won!
                child.close()
                return True, hist
            elif 'you lose' in bfr_txt: # we lost!
                child.close()
                return False, hist
            else: # unacceptable way to end the game!
                child.close()
                return 'Return error', hist
        elif 'please enter your next guess' in afr_txt: # this shows that the game is asking for the next guess
            if first_loop: # when in the ffirst loop we need to determine how many letters are in the word that we need to guess, remove all words from our word list that are not that length, update the hist['remaining_words_hist'] list and turn the first_loop variable to false so this process is skipped for other iterations of the loop
                no_of_letters = bfr_txt.count('*')
                first_loop = False
                remaining_words = [word for word in all_words if len(word) == no_of_letters]
                hist['remaining_words_hist'].append(remaining_words)

            word_progress = bfr_txt[-no_of_letters:] # the last letters of this string should be the astericked word
            hist['word_progress_hist'].append(word_progress) # update hist
            if word_progress.count('*') == len(word_progress): # this means that we have made no correct guesses yet and so we know that a vowel must exist in the word
                try:
                    vowel = vowel_list.pop(0) # guess a vowel that has not already been guessed
                except: # if an error occurs then it must mean the list is empty which means that either the word we are trying to guess does not have a vowel in (which is impossible if they are using the correct word list) or the game is not processing our guesses correctly
                    child.close()
                    return 'Vowel error', hist

                child.sendline(vowel) # send our guess to the game
                hist['guess_hist'].append(vowel) # update hist
            else: # if here then we must have guessed atleast one letter correctly.
                idx_to_letter_dict = {idx: word_progress[idx] for idx in range(len(word_progress)) if word_progress[idx] != '*'} # dictionary where the keys are the indexes of the word string that have been guessed correctly and the values are the corresponding letter
                remaining_words = [word for word in remaining_words if ( sum([word[idx] == idx_to_letter_dict[idx] for idx in idx_to_letter_dict.keys()]) == len([word[idx] == idx_to_letter_dict[idx] for idx in idx_to_letter_dict.keys()]) ) ] # this removes words from the remaining word list that don't match our guesses
                hist['remaining_words_hist'].append(remaining_words) # update hist
                letter_occurences = {letter: 0 for letter in all_letters} # create a dict that will count all the letter frequencies from the remainind words list so that we can decide which letter is most likely to be correct on our next guess
                for word in remaining_words:
                    for letter in word:
                        letter_occurences[letter] += 1

                letters_by_occurence = sorted(letter_occurences.items(), key = lambda kv: kv[1], reverse = True) # order it so that the letters that occur the most occur at the the top of the list
                hist['letters_by_occurence_hist'].append(letters_by_occurence) # update hist
                for letter_tuple in letters_by_occurence: # we want to guess the letter with the highest frequency but we might have already correctly guessed that letter so we want to skip the ones that have already been guessed
                    if letter_tuple[0] not in word_progress:
                        tmp_guess = letter_tuple[0]
                        break

                child.sendline(tmp_guess) # send our next guess to the hangman game
                hist['guess_hist'].append(tmp_guess) # update hist
        else: # if here then the game has stopped without ending the game corerctly or asking for a new guess which is stated in the instructions
            child.close()
            return 'EOF/input error', hist

def solveGameWord(file_path, word):
    """
    This is a function similar to solveGame except that the student's game asks for the word that needs to be guessed. This was used in the development stage and is unlikely to be needed again but is here for completeness but i have not bothered to comment etc.
    """
    hist = {'word': word, 'guess_hist': [], 'word_progress_hist': [], 'remaining_words_hist': [], 'letters_by_occurence_hist': []}
    all_letters = 'abcdefghijklmnopqrstuvwxyz'
    consonants = 'bcdfghjklmnpqrstvwxz'
    vowels = 'aeiouy'
    vowel_list = [vowel for vowel in vowels]
    try:
        child = pexpect.spawn('python -c "import ' + file_path[:-3] + ';print(' + file_path[:-3] + '.playGame(\'' + word + '\'))')
    except:
        child.close()
        return 'Spawn error', hist
    #child = pexpect.run('python ' + file_path)
    finished_flag = False
    first_loop = True
    while not finished_flag:
        try: 
            child.expect(['Please enter your next guess: ', pexpect.EOF])
        except:
            child.close()
            return 'Expect error', hist

        try:
            bfr_txt = child.before.decode().strip().lower()
            bfr_txt = " ".join(bfr_txt.split())
        except:
            child.close()
            return 'bfr decode error', hist
        try:
            afr_txt = child.after.decode().strip().lower()
            afr_txt = " ".join(afr_txt.split())
        except:
            if child.after == pexpect.EOF:
                afr_txt = child.after
            else:
                child.close()
                return 'afr decode error', hist
        if afr_txt is pexpect.EOF:
            if 'congratulations you win' in bfr_txt:
                child.close()
                return True, hist
            elif 'you lose' in bfr_txt:
                child.close()
                return False, hist
            else:
                child.close()
                return 'Return error', hist
        elif 'please enter your next guess' in afr_txt:
            if first_loop:
                no_of_letters = bfr_txt.count('*')
                first_loop = False
                remaining_words = [word for word in all_words if len(word) == no_of_letters]
                hist['remaining_words_hist'].append(remaining_words)

            word_progress = bfr_txt[-no_of_letters:]
            hist['word_progress_hist'].append(word_progress)
            if word_progress.count('*') == len(word_progress):
                try:
                    vowel = vowel_list.pop(0)
                except:
                    child.close()
                    return 'Vowel error', hist

                child.sendline(vowel)
                hist['guess_hist'].append(vowel)
            else:
                idx_to_letter_dict = {idx: word_progress[idx] for idx in range(len(word_progress)) if word_progress[idx] != '*'}
                remaining_words = [word for word in remaining_words if ( sum([word[idx] == idx_to_letter_dict[idx] for idx in idx_to_letter_dict.keys()]) == len([word[idx] == idx_to_letter_dict[idx] for idx in idx_to_letter_dict.keys()]) ) ]
                hist['remaining_words_hist'].append(remaining_words)
                letter_occurences = {letter: 0 for letter in all_letters}
                for word in remaining_words:
                    for letter in word:
                        letter_occurences[letter] += 1

                letters_by_occurence = sorted(letter_occurences.items(), key = lambda kv: kv[1], reverse = True)
                hist['letters_by_occurence_hist'].append(letters_by_occurence)
                for letter_tuple in letters_by_occurence:
                    if letter_tuple[0] not in word_progress:
                        tmp_guess = letter_tuple[0]
                        break

                child.sendline(tmp_guess)
                hist['guess_hist'].append(tmp_guess)
        else:
            child.close()
            return 'EOF/input error', hist

# the following code was used to test the accuracy of the algorithm on a 100 repetitions of 100 game tests (i.e. the script was tested 10,000 times). We found that the alforithm correctly guessed the word ~71% of the time
if __name__ == "__main__":
    file_name = 'OC_HM_iterative_words.py'

    results = []
    for it in tqdm.tqdm(range(100)): # show progress bar for 100 repetitions of the test
        rand_words = [all_words[random.randint(0, len(all_words) - 1)] for _ in range(100)] # generate random word list
        pool = mp.Pool()
        results.append(pool.starmap(solveGameWord, zip([file_name] * 100, rand_words))) # calculate 100 games in parallel
    with open('100x100_rand_results.pkl', 'wb') as f: # save the results as a pickle file
        pkl.dump(results, f)

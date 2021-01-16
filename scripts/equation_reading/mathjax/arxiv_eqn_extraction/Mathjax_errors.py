import os
import subprocess
import json
import matplotlib.pyplot as plt

from datetime import datetime
from operator import itemgetter
from collections import OrderedDict

print('starting at:  ', datetime.now())

def main():

    root = '/projects/temporary/automates/er/gaurav/'

    for yr in [14]:#, 15, 16, 17, 18]:

        year = '20' + str(yr)

        print(' ==++== ' *10)
        print('Currently working on logs file of:  ', year)

        # make directory 'combine logs' -- to store all of the results
        combine_logs_path = os.path.join(root, f'{year}/Logs/combine_logs')
        if not os.path.exists(combine_logs_path):
            subprocess.call(['mkdir', combine_logs_path])

        logs_path = os.path.join(root, f'{year}/Logs/combine_logs/{year}_MathJax_MML_Log.log')

        (dict_token, dict_error, token_counter, error_counter) = Mjx_errors_and_not_working_tokens(logs_path)

        # dumping token/error dictionaries in the form of tuples ordered by values
        json.dump(OrderedDict(sorted(dict_token.items(), key=itemgetter(1))),
                open(os.path.join(root, f'{year}/Logs/combine_logs/not_working_tokens_tuples.json'), 'w'))
        json.dump(OrderedDict(sorted(dict_error.items(), key=itemgetter(1))),
                open(os.path.join(root, f'{year}/Logs/combine_logs/Mathjax_errors_tuples.json'),'w'))

        # ranking tokens/errors based on the total number of equations affected
        (sorted_token_counter_tuples, sorted_error_counter_tuples, top10_tokens_tuples, top10_errors_tuples) = Ranking(token_counter, error_counter)

        # dumping counter dictionaries in the form of tuples ordered by values
        json.dump(sorted_token_counter_tuples, open(os.path.join(root, f'{year}/Logs/combine_logs/tokens_counter_tuples.json'),'w'))
        json.dump(Osorted_error_counter_tuples, open(os.path.join(root, f'{year}/Logs/combine_logs/errors_counter_tuples.json'), 'w'))
        json.dump(top10_tokens_tuples, open(os.path.join(root, f'{year}/Logs/combine_logs/top10_tokens_tuples.json'),'w'))
        json.dump(top10_errors_tuples, open(os.path.join(root, f'{year}/Logs/combine_logs/top10_errors_tuples.json'), 'w'))

        # finding histogram distribution of token/error counter dictionaries
        # It helps to get an idea of the errors/tokens that are affecting most of the eqns
        Distribution(root, year, sorted_token_counter_tuples, sorted_error_counter_tuples, top10_tokens_tuples, top10_errors_tuples)


# finding 'not working' latex eqns and respective tokens
# These tokens can be find in the lines having 'is either not supported by
# MathJax or incorrectly written'

def Mjx_errors_and_not_working_tokens(log_file):

    # defining dictionary to store 'not working' eqns along with respective
    # tokens -- {latex_eqns:token} or errors -- {latyex_eqns:error}
    dict_token = {}
    dict_error = {}

    # defining a dictionary to keep record of the frequency of a token or error
    # {token/error: total number of equations it has affected}
    token_counter = {}
    error_counter = {}

    # reading log data
    data = open(log_file ,'r').readlines()

    for line in data:

        # eqn_path: will tell us the equation's tex_file path
        # sentence: will be in the form -- '<token> is either not supported by
        # MathJax or incorrectly written' or  '<error> is an error produced by MathJax webserver'
        (eqn_path, sentence) = line.split(':')[1], line.split(':')[-1]

        # PART 1 -- COLLECT ALL THE 'NOT WORKING' TOKENS
        if 'is either not supported by MathJax or incorrectly written' in sentence:

            #print('Part 1 --  ', line.split(':'))

            eqn_path = eqn_path.replace('latex_images', 'tex_files')
            #latex_eqn = open((eqn_path+'.txt'), 'r').readlines()[0]
            token = sentence.replace(' is either not supported by MathJax or incorrectly written', '').replace(' ', '')

            # Appending the list of the eqn_paths for respective token
            if token in dict_token.keys():
                if eqn_path not in dict_token[token]:
                    dict_token[token].append(eqn_path)

            else:
                dict_token[token] = [eqn_path]

            # to record the frequency of the token
            if token in token_counter.keys():
                token_counter[token] +=1
            else:
                token_counter[token] = 1

        # PART 2 -- COLLECT ALL THE 'ERRORS' PRODUCED BY MATHJAX SERVER
        if 'is an error produced by MathJax webserver' in sentence:

            #print('Part 2 --  ', line.split(':'))

            eqn_path = eqn_path.replace('latex_images', 'tex_files')
            #latex_eqn = open((eqn_path+'.txt'), 'r').readlines()[0]
            error = sentence.replace(' is an error produced by MathJax webserver', '').replace(' ', '')

            # Appending the list of the eqn_paths for respective Mathjax error
            if error in dict_error.keys():
                if eqn_path not in dict_error[error]:
                    dict_error[error].append(eqn_path)

            else:
                dict_error[error] = [eqn_path]

            # to record the frequency of the error
            if error in error_counter.keys():
                error_counter[error] +=1
            else:
                error_counter[error] = 1

    return(dict_token, dict_error, token_counter, error_counter)


def Ranking(token_counter, error_counter):

    print('Ranking now')

    # Sorted counters
    sorted_token_counter_tuples = OrderedDict(sorted(token_counter.items(), key=itemgetter(1)))
    sorted_error_counter_tuples = OrderedDict(sorted(error_counter.items(), key=itemgetter(1)))

    # getting most common/top 10 tokens/errors by value
    top10_tokens_tuples = dict(sorted(sorted_token_counter.items(), key = itemgetter(1), reverse = True)[:10])
    top10_errors_tuples = dict(sorted(sorted_error_counter.items(), key = itemgetter(1), reverse = True)[:10])

    return(sorted_token_counter_tuples, sorted_error_counter_tuples, top10_tokens_tuples, top10_errors_tuples)


def Distribution(root, year, sorted_token_counter_tuples, sorted_error_counter_tuples, top10_tokens_tuples, top10_errors_tuples):

    print('Distribution')

    # histograms of token_counter
    plt.figure(figsize=(30,10))
    # sort in-place from highest to lowest
    sorted_token_counter_tuples.sort(key=lambda x: x[1], reverse=True)

    # save the tokens/errors and their respective scores separately
    # reverse the tuples to go from most frequent to least frequent
    tokens = zip(*sorted_token_counter_tuples)[0]
    score_tokens = zip(*sorted_token_counter_tuples)[1]
    x_pos_tokens = np.arange(len(tokens))
    plt.bar(x_pos_tokens, score_tokens, align='center', color='g')
    plt.xticks(x_pos_tokens, tokens , rotation=90)
    plt.savefig(os.path.join(root, f'{year}/Logs/combine_logs/token_histogram.png'))

    # histograms of error_counter
    plt.figure(figsize=(30,10))
    # sort in-place from highest to lowest
    sorted_error_counter_tuples.sort(key=lambda x: x[1], reverse=True)

    # save the tokens/errors and their respective scores separately
    # reverse the tuples to go from most frequent to least frequent
    errors = zip(*sorted_error_counter_tuples)[0]
    score_errors = zip(*sorted_error_counter_tuples)[1]
    x_pos_errors = np.arange(len(errors))
    plt.bar(x_pos_errors, score_errors, align='center', color='b')
    plt.xticks(x_pos_errors, errors , rotation=90)
    plt.savefig(os.path.join(root, f'{year}/Logs/combine_logs/error_histogram.png'))

    # histograms of top10_token
    plt.figure(figsize=(30,10))
    # sort in-place from highest to lowest
    top10_tokens_tuples.sort(key=lambda x: x[1], reverse=True)

    # save the tokens/errors and their respective scores separately
    # reverse the tuples to go from most frequent to least frequent
    top10_tokens = zip(*top10_tokens_tuples)[0]
    top10_score_tokens = zip(*top10_tokens_tuples)[1]
    x_pos_top10_tokens = np.arange(len(top10_tokens))
    plt.bar(x_pos_top10_tokens, top10_score_tokens, align='center', color='g')
    plt.xticks(x_pos_top10_tokens, top10_tokens , rotation=90)
    plt.savefig(os.path.join(root, f'{year}/Logs/combine_logs/top10_token_histogram.png'))

    # histograms of top10_errors
    plt.figure(figsize=(30,10))
    # sort in-place from highest to lowest
    top10_errors_tuples.sort(key=lambda x: x[1], reverse=True)

    # save the tokens/errors and their respective scores separately
    # reverse the tuples to go from most frequent to least frequent
    top10_errors = zip(*top10_errors_tuples)[0]
    top10_score_errors = zip(*top10_errors_tuples)[1]
    x_pos_top10_errors = np.arange(len(top10_errors))
    plt.bar(x_pos_top10_errors, top10_score_errors, align='center', color='b')
    plt.xticks(x_pos_top10_errors, top10_errors , rotation=90)
    plt.savefig(os.path.join(root, f'{year}/Logs/combine_logs/top10_error_histogram.png'))

if __name__ == "__main__":
    main()

    print('stopping at:  ', datetime.now())

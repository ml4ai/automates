import os
import subprocess
import fileinput
import json

# re-arranging the logs
def rearranging_logs():

    root = '/projects/temporarty/automates/er/gaurav'
    year_list = [18]

    for yr in year_list:

        year = '20'+str(yr)
        logs_path = os.path.join(root, f'{year}/Logs')

        # Selecting Mathjax_mml logs
        temp = []
        for logFiles in os.listdir(logs_path):
            if 'MathJax_MML_newLock' in logFiles:
                temp.append(logFiles)

        # open and read the files -- merge them together
        os.chdir(logs_path)
        log_data = list(fileinput.input(temp))

        # filtering WARNING from log_data
        WARNING_list = list()

        for line in log_data:
            if line.split(':')[0] == 'WARNING':
                WARNING_list.append(line)

        # re-writing list at the respective destination folder
        new_log_path = os.path.join(logs_path, f'{year}_MathJax_MML_Log.log'}
        with open(new_log_path, 'w') as FILE:
            json.dump(WARNING_list, FILE)

# calling rearranging_logs function
rearranging_logs()

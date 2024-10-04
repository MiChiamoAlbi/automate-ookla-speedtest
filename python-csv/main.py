
# By Jamie Pond -- Github: jamierpond
#
# Improved by Alberto -- Github: MiChiamoAlbi
# changes: the header is inserted automatically, checks that the "download" data appears in the same position with respect to the file if present

import subprocess
import datetime
import time
import os
from csv import writer, reader

def get_time_str(num_seconds_elapsed):
    return time.strftime("%Hh %Mm %Ss", time.gmtime(num_seconds_elapsed))

def clean_data(data):
    data_list = data.split(',')
    processed_data = []
    for item in data_list:
        item = item.strip('"')
        if item.isdigit():
            processed_data.append(int(item))
        else:
            try:
                processed_data.append(float(item))
            except ValueError:
                processed_data.append(item)
    return processed_data

def ookla_test(output_csv, n_test_run, interval_seconds, seconds_to_run_for):
    print("Estimated running time: ", get_time_str(seconds_to_run_for))
    print("Tests to run: ", n_test_run)

    num_errors = 0

    # checks the existence of the output file, if it exists it checks the header that should correspond to the new header format (in case of update of format); 
    # if it does not exist it creates it
    try:
        with open(output_csv, 'r', newline='') as f:
            file_read = list(reader(f, delimiter=","))
            if file_read:
                header = file_read[0]
                empty_file = False
                try:
                    download_index_file = header.index('download')
                    continue_flag = True
                
                except:
                    print('Bad file - "download" not present in the header')
                    continue_flag = False
            else:
                empty_file = True
                continue_flag = True

    except:
        print(f'New file created: {output_csv}')
        continue_flag = True
        empty_file = True

    # search for the ookla.exe path
    if continue_flag:
        ookla_name = f'speedtest.exe'
        script_dir = os.path.dirname(os.path.abspath(__file__))
        same_py_path = os.path.join(script_dir, ookla_name)
        git_folder = os.path.join(os.path.dirname(script_dir), ookla_name)
        if os.path.isfile(same_py_path):
            exe_path = same_py_path
        elif os.path.isfile(git_folder):
            exe_path = git_folder
        else:
            print("Couldn't find ookla 'speedtest.exe'")
            continue_flag = False

    # if there have been no errors in the file already present, it inserts the data at the end of the file
    if continue_flag:
        with open(output_csv, 'a', newline='') as f_object:
            writer_object = writer(f_object)
        
            for i in range(int(n_test_run)):
                time_now = datetime.datetime.now().isoformat(' ', timespec='seconds')
                print(f"Test {i+1}/{n_test_run} - {time_now}", end='', flush=True)

                if i == 0 or i == num_errors:
                    settings = exe_path + " --format=csv --output-header --unit=Mbps"
                else:
                    settings = exe_path + " --format=csv --unit=Mbps"

                try:
                    output = subprocess.check_output(settings)
                except:
                    output = None

                # on the first iteration it inserts the header if absent and checks the download location for shell printing
                if output and i == num_errors:
                    header, values = output.decode('utf-8')[:-2].split('\r\n')

                    headeer_list = [item.strip('"') for item in header.split(',')]
                    headeer_list.insert(0, 'date')
                    download_index = headeer_list.index("download")
                    
                    if empty_file:
                        writer_object.writerow(headeer_list)

                    else:
                        if download_index_file != download_index:
                            print(' - The header is changed from the last time you used ookla')
                            break

                    # if there were errors before inserting the header, it calculates the time at which they occurred and inserts it afterwards
                    for error in range(num_errors):
                        time_error = (datetime.datetime.now() - datetime.timedelta(seconds=interval_seconds*((num_errors + 1) - error))).isoformat(' ', timespec='seconds')
                        writer_object.writerow([time_error,'Connection Error'])
                    
                    values_list = clean_data(values)

                    values_list.insert(0, time_now)
                    writer_object.writerow(values_list)

                    print(f' - OK - Download speed: {values_list[download_index] / 125000} Mbps')

                elif output:
                    values_list = clean_data(output.decode('utf-8')[:-2])

                    print(f' - OK - Download speed: {values_list[download_index] / 125000} Mbps')

                    values_list.insert(0, time_now)
                    writer_object.writerow(values_list)
                    
                else:
                    num_errors += 1
                    print(f' - Connection Error')
                    # if left like this, i is always late on num_errors by 1, the counter after the if could be moved, but I don't like it
                    if i != num_errors - 1:
                        writer_object.writerow([time_now ,'Connection Error'])
            
                if i<int(n_test_run)-1:
                    f_object.flush()
                    time.sleep(interval_seconds)

            print("Finished testing!")


if __name__ == '__main__':
    # Edit the values you want before you run the script here.
    # I've had success with even appending to files on my remote
    # Google Drive (so many computers can feed into the same database!)
    output_csv_name         = r"speedtest_output.csv"
    interval_seconds    = 120
    hours_to_run_for    = 3
    minutes_to_run_for  = 0
    secondes_to_run_for = 0
    seconds_to_run_for = hours_to_run_for * 60 + minutes_to_run_for * 60 + secondes_to_run_for * 60

    n_test_run = int(seconds_to_run_for/interval_seconds)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_csv = os.path.join(script_dir, '..', 'results', output_csv_name)

    ookla_test(output_csv, n_test_run, interval_seconds, seconds_to_run_for)
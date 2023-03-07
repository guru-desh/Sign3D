# This script runs on the boss computers to control the employee computers

# Using the pexpect library to SSH into a remote machine and run a python script on it.
from pexpect import pxssh

# Using threading to run multiple commands on different SSH sessions at the same time
import threading

# Define this before running the script. Contains all the information about the employee computers needed for SSH
# TODO: Use private keys instead of passwords so we don't have to store passwords in plain text.
# TODO for Guru: The IP Addresses keep changing. It's affecting ASL QA too. Go talk to Tim about this.
employees = {
    'IP_ADDRESS_1': {
        'username': 'password',
    },
    'IP_ADDRESS_2': {
        'username': 'password',
    }
}

# Create a dictionary of SSH sessions
ssh_clients = {}
for i, ip, credentials in enumerate(employees.items()):
    # Create a new SSH session
    ssh_clients[ip] = pxssh.pxssh()
    
    # Try to SSH into the remote machine. If it fails, print the error and exit.
    try:
        ssh_clients[ip].login(ip, credentials['username'], credentials['password'])
    except pxssh.ExceptionPxssh as e:
        print(e)
        print(f"pxssh failed on login for employee{i} with ip address {ip}.")
        print("Exiting...")
        exit()

# Run the python script on all the remote machines. Can also run additional bash commands here.
# TODO: Add additional commands based on the recording script (not sure where that is)
for ip in ssh_clients.keys():
    ssh_clients[ip].sendline('python RECORDING.py')

# Wait for all the employees to be ready to record
readiness = []
for ip in ssh_clients.keys():
    readiness.append(ssh_clients[ip].expect('Hello', timeout=10))

# If not all employees are ready to record by the timeout, print an error message and exit. 
# TODO: Come up with better error messages about which employees are not ready to record and why.
if not all(readiness):
    print("Not all employees are ready to record within the timeout.")
    print("Aborting...")
    exit()
    
# Wait for the user to press enter to start recording
print("All employees are ready to record.")
input("Press enter to start recording.")

# Create a list of threads to start recording on all the remote machines at the same time.
# TODO: It's possible to do all of the SSH stuff and preliminary commands in the threads themselves. Should we do that?
threads = []
for ip in ssh_clients.keys():
    threads.append(threading.Thread(target=ssh_clients[ip].sendline, args=("SOMETHING",)))

# Start recording on all the remote machines at the same time.
print("Recording has started.")
for thread in threads:
    thread.start()

# Wait for the recording to end.
# TODO: Understand about how recording will end and how to handle that.
for thread in threads:
    thread.join()

print("Recording has ended.")

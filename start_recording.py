# This script runs on the boss computers to control the employee computers

# Using the pexpect library to SSH into a remote machine and run a python script on it.
from pexpect import pxssh

# Using threading to run multiple commands on different SSH sessions at the same time
import threading

# Define this before running the script. Contains all the information about the employee computers needed for SSH
with open('password.txt', 'r') as f:
    password = f.read().strip()

employees = {
    '100.70.35.117': (
        'tsrb243', password
    )
}
# Create a dictionary of SSH sessions
ssh_clients = {}

count = 0
for ip, credentials in employees.items():
    print(ip, credentials)
    # Create a new SSH session
    ssh_clients[ip] = pxssh.pxssh(encoding='utf-8')
    
    # Try to SSH into the remote machine. If it fails, print the error and exit.
    try:
        ssh_clients[ip].login(ip, credentials[0], credentials[1])
    except pxssh.ExceptionPxssh as e:
        print(e)
        print(f"pxssh failed on login for employee{count} with ip address {ip}.")
        print("Exiting...")
        exit()
    count += 1
    
# Run the python script on all the remote machines.
for ip in ssh_clients.keys():
    ssh_clients[ip].sendline('cd MultiCam/ && conda activate maac && export DISPLAY=:0.0 && python3 record.py')  

# Wait for all the employees to be ready to record
readiness = []
for ip in ssh_clients.keys():
    try:
        success = ssh_clients[ip].expect('Ready to Record', timeout=3)
        readiness.append(True)
    except pxssh.TIMEOUT:
        print("Not all employees are ready to record within the timeout.")
        print("Aborting...")
        exit()

# Wait for the user to press enter to start recording
print("All employees are ready to record.")
input("Press enter to start recording.")

threads = []
for ip in ssh_clients.keys():
    threads.append(threading.Thread(target=ssh_clients[ip].sendline, args=("Enter",)))

# Start recording on all the remote machines at the same time.
print("Recording has started.")
for thread in threads:
    thread.start()
    
for thread in threads:
    thread.join()

# TODO: Handle ending the script
input("Press enter to end recording:\n")
threads = []
for ip in ssh_clients.keys():
    # Send a ctrl-c to end the recording to all the remote machines at the same time.
    threads.append(threading.Thread(target=ssh_clients[ip].sendcontrol, args=("c",)))

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

print("Recording has ended.")

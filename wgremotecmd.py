
import paramiko, multiprocessing

import json

def ssh_connecation(host, username, private_key_path):
   
        # Initialize an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
                ssh.connect(host, username=username, key_filename=private_key_path)
                ssh.close()
                return True 
        except Exception as e:
                return False  # SSH connection failed for at least one host

 # All SSH connections were successful

def check_ssh_connections(hosts, username, private_key_path):
    results = []
    processes = []

    # Create a multiprocessing Pool
    pool = multiprocessing.Pool(processes=len(hosts))

    try:
        # Map the execute_ssh_command function to each host with common arguments
        for host in hosts:
            process = pool.apply_async(ssh_connecation, (host, username, private_key_path))
            processes.append(process)

        # Wait for all processes to complete and retrieve their results
        pool.close()
        pool.join()

        # Retrieve results from the completed processes
        for process in processes:
            result = process.get()
            results.append(result)
        if all(results):
            return True
        else:
            return False

    except Exception as e:
        results.append({"error": str(e)})

      



def execute_ssh_command(host, username, private_key_path, command):
        results = []  # Create a list to store the results for each host
        try:
            # Initialize an SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the remote host using the provided username and private key
            ssh.connect(host, username=username, key_filename=private_key_path)

            # Execute the SSH command
            stdin, stdout, stderr = ssh.exec_command(command)

            # Read the command output and error
            command_output = stdout.read().decode('utf-8')
            error_output = stderr.read().decode('utf-8')

            # Close the SSH connection
            ssh.close()

            try:
                results.append(command_output)
            except json.JSONDecodeError:
                results.append({"error": "Failed to parse JSON response from the tool"})

        except Exception as e:
            results.append({"error": str(e)})

        return results



import paramiko

import json

def check_ssh_connections(hosts, username, private_key_path):
    try:
        # Initialize an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        for host in hosts:
            try:
                ssh.connect(host, username=username, key_filename=private_key_path)
                ssh.close()
            except Exception as e:
                return False  # SSH connection failed for at least one host

        return True  # All SSH connections were successful
    except Exception as e:
        return False  # Exception occurred



def execute_ssh_command(hosts, username, private_key_path, command):
    results = []  # Create a list to store the results for each host

    for host in hosts:
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


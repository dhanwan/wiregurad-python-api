import subprocess
import re

def execute_backup_script():
    try:
        script_path = 'script/backup.sh'
        
        # Execute the Bash script
        subprocess.run(['/bin/bash', script_path], check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error executing the backup script: {e}")
    except FileNotFoundError:
        print("Backup script not found. Make sure the path is correct.")

def check_string_in_file(file_path, target_string):
    try:
        with open(file_path, 'r') as file:
            file_contents = file.read()
            if target_string in file_contents:
                return "true"
            else:
                return "false"
    except FileNotFoundError:
        return "File not found"
    except Exception as e:
        return f"An error occurred: {str(e)}"

    
def restart_wg():
    command = "/usr/bin/systemctl restart wg-quick@wg0.service"
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
    
# Add a wiregurad Public key API

def validate_ipv4(ipv4):
    # Define a regular expression pattern for IPv4 addresses
    ipv4_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')

    # Check if the input matches the pattern
    return bool(ipv4_pattern.match(ipv4))

def validate_wireguard_public_key(public_key):
    # Define a regular expression pattern for a WireGuard public key
    wireguard_key_pattern = re.compile(r'^[A-Za-z0-9+/]{43}=$')

    # Check if the input matches the pattern
    return bool(wireguard_key_pattern.match(public_key))

def remove_trailing_newline(publickey):
    # Use rstrip to remove trailing newline characters
    return publickey.rstrip('\n')

def validate_ip_key(key,ip):
    status = {}
    print("validating the Publickey")
    
    if validate_wireguard_public_key(key):
        if validate_ip_key(ip):
            status['validate'] = True
        else:
            status['validate'] = False
    else:
        status['validate'] = False
        
    return status

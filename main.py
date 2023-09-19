from flask import Flask, request, Response
import subprocess
import re
app = Flask(__name__)

# Taking backup of existing file

wgconf = "/etc/wireguard/wg0.conf"

def execute_backup_script():
    try:
        script_path = 'script/backup.sh'
        
        # Execute the Bash script
        subprocess.run(['/bin/bash', script_path], check=True)

        print("Backup completed successfully.")
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
        print("wiregurad restarted")
    except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
    
# Add a wiregurad Public key API

def validate_ipv4_with_cidr(ipv4):
    # Define a regular expression pattern for IPv4 with CIDR notation
    ipv4_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/(32|16|24)$')

    # Check if the input matches the pattern
    return bool(ipv4_pattern.match(ipv4))
 
@app.route('/api/wireguard/adduser', methods=['POST'])
def AddUser():
    data = request.json

    if "key" in data and "ipv4" in data:
        public_key = data["key"]
        allowed_ips = data["ipv4"]
        if not validate_ipv4_with_cidr(allowed_ips):
            return Response("Invalid IPv4 format. Please provide a valid IPv4 address.", status=400)

        checks = check_string_in_file(wgconf, public_key)
        ipcks = check_string_in_file(wgconf, allowed_ips)
        if checks == "false" :
            if ipcks == "false":

                print("Taking backup of existing wg0.conf file")
                execute_backup_script()

                print("add key and ips to wg0.conf file")
                command = f"/usr/bin/wg set wg0 peer {public_key} allowed-ips {allowed_ips}"

                try:
                    subprocess.run(command, shell=True, check=True)
                    print(f"Successfully added allowed IP {allowed_ips} for peer {public_key}")
                except subprocess.CalledProcessError as e:
                    print(f"Error: {e}")
                restart_wg()  
                # append_key_to_file(wgconf, content)

                response_message = "User added successfully."
                return Response(response_message)
            else:
                return Response("user Ip already exists Pls use different ip")
                
        else:
            return Response("Users Public key already exists", status=200)

    else:
        return Response("Missing 'key' or 'ipv4' fields in the JSON data.", status=400)
    
    
#Remove the Wireguard Public key API
def remove_wireguard_peer(public_key, allowed_ips):
    try:
        # Assuming wgconf is the path to the wg0.conf file
        # wgconf = "/path/to/wg0.conf"

        # Check if the public key exists in wg0.conf
        if check_string_in_file(wgconf, public_key) == "true":
            # Check if allowed-ips exists in wg0.conf
            if check_string_in_file(wgconf, allowed_ips) == "true":
                print("Taking backup of existing wg0.conf file")
                execute_backup_script()

                print("Removing key and ips from wg0.conf file")
                command = f"/usr/bin/wg set wg0 peer {public_key} remove allowed-ips {allowed_ips}"  
                subprocess.run(command, shell=True, check=True)
                restart_wg()
            else:
                return Response("User Allowed-ips not found in server", status=400)
        else:
             return Response("User Public key not found in wg0.conf", status=400)
        
        return Response("user successfully removed", status=200)
    except Exception as e:
        return Response(str(e), status=500)

@app.route('/api/wireguard/remove', methods=['POST'])

def remove_user():
    data = request.json
    if "key" in data and "ipv4" in data:
        public_key = data["key"]
        allowed_ips = data["ipv4"]
        if not validate_ipv4_with_cidr(allowed_ips):
            return Response("Invalid IPv4 format. Please provide a valid IPv4 address.", status=400)
        else:
            return remove_wireguard_peer(public_key, allowed_ips)
    else:
        return Response("Please provide key and ipv4 value", status=400)


    
        
if __name__ == "__main__":
    app.run(host='0.0.0.0')
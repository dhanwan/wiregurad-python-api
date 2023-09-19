from flask import Flask, request, Response, jsonify
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
 
@app.route('/api/wireguard/adduser', methods=['POST'])
def AddUser():
    data = request.json

    if "key" in data and "ipv4" in data:
        public_key = data["key"].strip()
        allowed_ips = data["ipv4"].strip()
        public_key = remove_trailing_newline(public_key)
        if not validate_wireguard_public_key(public_key):
            response_message = {"status": 400, "message": "Pls provide a valid publickey for users", "success": False}
            return jsonify(response_message)

        if not validate_ipv4(allowed_ips):
            response_message = {"status": 400, "message": "Invalid IPv4 format. Please provide a valid IPv4 address.", "success": False}
            return jsonify(response_message)

        checks = check_string_in_file(wgconf, public_key)
        ipcks = check_string_in_file(wgconf, allowed_ips)
        if checks == "false" :
            if ipcks == "false":
                print("Taking backup of existing wg0.conf file")
                execute_backup_script()

                print("add key and ips to wg0.conf file")
                command = f"/usr/bin/wg set wg0 peer {public_key} allowed-ips '{allowed_ips}'"

                try:
                    subprocess.run(command, shell=True, check=True)
                    print(f"Successfully added allowed IP '{allowed_ips}' for peer {public_key}/32")
                except subprocess.CalledProcessError as e:
                    print(f"Error: {e}")
                restart_wg()  

                response_message = {"status": 200, "message": "User added successfully.", "success": True}
                return jsonify(response_message)
            else:
                response_message = {"status": 400, "message": "user Ip already exists Pls use different ip.", "success": False}
                return jsonify(response_message)
                
        else:
            response_message = {"status": 200, "message": "Users Public key already exists", "success": True}
            return jsonify(response_message)

    else:
        response_message = {"status": 400, "message": "Missing 'key' or 'ipv4' fields in the JSON data.", "success": False}
        return jsonify(response_message)
    
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
                command = f"/usr/bin/wg set wg0 peer {public_key} remove allowed-ips '{allowed_ips}/32'"  
                subprocess.run(command, shell=True, check=True)
                restart_wg()
                response_message = {"status": 200, "message": "User successfully removed.", "success": True}
                return jsonify(response_message)
            else:
                response_message = {"status": 400, "message": "User Allowed-ips not found in server.", "success": False}
                return jsonify(response_message)
        else:
             response_message = {"status": 400, "message": "User Public key not found in wg0.conf.", "success": False}
             return jsonify(response_message)
        
    except Exception as e:
        response_message = {"status": 500, "message": str(e), "success": False}
        return jsonify(response_message)

@app.route('/api/wireguard/remove', methods=['POST'])

def remove_user():
    data = request.json
    if "key" in data and "ipv4" in data:
        public_key = data["key"].strip()
        allowed_ips = data["ipv4"].strip()
        key = remove_trailing_newline(public_key)
        if not validate_ipv4(allowed_ips):
            response_message = {"status": 400, "message": "Invalid IPv4 format. Please provide a valid IPv4 address.", "success": False}
            return jsonify(response_message)
        else:
            return remove_wireguard_peer(key, allowed_ips)
    else:
        response_message = {"status": 400, "message": "Please provide key and ipv4 value", "success": False}
        return jsonify(response_message)


    
        
if __name__ == "__main__":
    app.run(host='0.0.0.0')
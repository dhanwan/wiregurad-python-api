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
    
# Add a wiregurad Public key API
 
@app.route('/api/wireguard/adduser', methods=['POST'])
def AddUser():
    data = request.json

    if "key" in data and "ipv4" in data:
        public_key = data["key"]
        allowed_ips = data["ipv4"]

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
                    
                # append_key_to_file(wgconf, content)
                command = "/usr/bin/systemctl restart wg-quick@wg0.service"

                subprocess.run(command, shell=True, check=True)

                response_message = "Public key added successfully."
                return Response(response_message)
            else:
                return Response("Ip already exists Pls use different ip")
                
        else:
            return Response("Public key already exists", status=200)

    else:
        return Response("Missing 'key' or 'ipv4' fields in the JSON data.", status=400)
    
    
#Remove the Wireguard Public key API

    
@app.route('/api/wireguard/remove', methods=['POST'])
def RemoveUser():
    data = request.json
    if "key" in data and "ipv4" in data:
        public_key = data["key"]
        allowed_ips = data["ipv4"]
        
        checks = check_string_in_file(wgconf, public_key)
        ipcks = check_string_in_file(wgconf, allowed_ips)
        if checks == "false" :
            if ipcks == "false":
                print("Taking backup of existing wg0.conf file")
                execute_backup_script()

                print("Remove key and ips from wg0.conf file")
                command = f"/usr/bin/wg set wg0 peer {public_key} remove allowed-ips {allowed_ips}"  
                subprocess.run(command, shell=True, check=True)

            else:
                return Response("Allowed-ips not found in wg0.conf")
        else:
            return Response("Public not found")

    
    return Response("Remove user")
        

    return Response(response_message, status=200)
if __name__ == "__main__":
    app.run(host='0.0.0.0')
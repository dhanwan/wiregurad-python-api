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

def append_key_to_file(file_path, content):
    try:
        with open(file_path, "a") as file:
            file.write(content)
        print(f"Content appended to {file_path}")
    except Exception as e:
        print(f"Error appending content to {file_path}: {str(e)}")

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
        print(checks)
        if checks == "false" :
            print("Taking backup of existing wg0.conf file")
            execute_backup_script()

            print("add key and ips to wg0.conf file")
            content = f"\n[Peer]\nPublicKey = {public_key}\nAllowedIPs = {allowed_ips}"
            append_key_to_file(wgconf, content)
            command = ["/usr/bin/systemctl", "restart ","wg-quick@wg0.service"]
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            response_message = "Public key added successfully."
            return Response(response_message)
        else:
            return Response("Public key already exists", status=200)

    else:
        return Response("Missing 'key' or 'ipv4' fields in the JSON data.", status=400)
    
    
#Remove the Wireguard Public key API

def remove_public_key(filename, public_key_to_remove):

    with open(filename, 'r') as file:
        config_text = file.read()


    pattern = r'\[Peer\]\nPublicKey = {}\nAllowedIPs = [^\n]+\n'.format(re.escape(public_key_to_remove))
    
 
    if re.search(pattern, config_text):
        # Use re.sub to remove the matched block
        modified_config = re.sub(pattern, '', config_text)

        # Write the modified content back to the file
        with open(filename, 'w') as file:
            file.write(modified_config)
            print("key add successfully")
    else:
        print( "Public key doesn't exist in the file.")
    
@app.route('/api/wireguard/remove', methods=['POST'])
def RemoveUser():
    data = request.json
    if "key" in data:
        public_key = data["key"]

        remove_public_key(wgconf, public_key)
    
    return Response("Remove user")
        

    return Response(response_message, status=200)
if __name__ == "__main__":
    app.run(host='0.0.0.0')
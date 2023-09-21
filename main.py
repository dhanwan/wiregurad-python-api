from flask import Flask, request, Response, jsonify
import wgvalidation, wgremotecmd, json 
app = Flask(__name__)

# Taking backup of existing file
username = 'root'
private_key_path = '/Users/ntf-m3/.ssh/id_rsa'
hosts = ['ca1.limevpn.com']

def beautify_json(json_string):
    try:
       
        json_string = json_string.strip()   
        json_string = json_string.replace("'", "\"")

        json_data = json.loads(json_string)
        beautified_json = json.dumps(json_data, indent=4)

        return beautified_json
    except json.JSONDecodeError as e:
        return f"Error: Failed to beautify JSON - {str(e)}"


@app.route('/api/wireguard/adduser', methods=['POST'])
def AddUser():
    data = request.json

    if "key" in data and "ipv4" in data:
        public_key = data["key"].strip()
        allowed_ips = data["ipv4"].strip()
        public_key = wgvalidation.remove_trailing_newline(public_key)
        keycheck = wgvalidation.validate_wireguard_public_key(public_key)
        IpCheck = wgvalidation.validate_ipv4(allowed_ips)
        if not keycheck:
            response_message = {"status": 400, "message": "Pls provide a valid publickey for users", "success": False}
            return jsonify(response_message)
        if not IpCheck:
            response_message = {"status": 400, "message": "Invalid IPv4 format. Please provide a valid IPv4 address.", "success": False}
            return jsonify(response_message)
    # Check SSH connections
        ssh_successful = wgremotecmd.check_ssh_connections(hosts, username, private_key_path)
      
        if ssh_successful:
            command = f"/mnt/wg_python/main.py -key {public_key} -ip {allowed_ips} -A add"
            responses = wgremotecmd.execute_ssh_command(hosts, username, private_key_path, command)
            json_reponse = beautify_json(responses)
            return jsonify(json_reponse)

        else:
            response_message = {"status": 200, "message": "Remote command execuation failed to vpn server pls check the server", "success": True}
            return jsonify(response_message)

  






            
    

@app.route('/api/wireguard/remove', methods=['POST'])

def remove_user():
            data = request.json
            public_key = data["key"].strip()
            allowed_ips = data["ipv4"].strip()

            public_key = wgvalidation.remove_trailing_newline(public_key)
            
            keycheck = wgvalidation.validate_wireguard_public_key(public_key)
            IpCheck = wgvalidation.validate_ipv4(allowed_ips)
            if not keycheck:
                response_message = {"status": 400, "message": "Pls provide a valid publickey for users", "success": False}
                return jsonify(response_message)
            if not IpCheck:
                response_message = {"status": 400, "message": "Invalid IPv4 format. Please provide a valid IPv4 address.", "success": False}
                return jsonify(response_message)
        # Check SSH connections
            ssh_successful = wgremotecmd.check_ssh_connections(hosts, username, private_key_path)
        
            if ssh_successful:
                command = f"/mnt/wg_python/main.py -key {public_key} -ip {allowed_ips} -A remove"
                responses = wgremotecmd.execute_ssh_command(hosts, username, private_key_path, command)
                responses = wgremotecmd.execute_ssh_command(hosts, username, private_key_path, command)
                json_reponse = beautify_json(responses)
                return jsonify(json_reponse)

            else:
                response_message = {"status": 200, "message": "Remote command execuation failed to vpn server pls check the server", "success": True}
                return jsonify(response_message)


    
        
if __name__ == "__main__":
    app.run(host='0.0.0.0')
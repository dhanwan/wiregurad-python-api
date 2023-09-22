#! /usr/bin/python3
import wgvalidation
import subprocess
import argparse
from platform import node

# Define command-line arguments
parser = argparse.ArgumentParser(description="Add a user to a WireGuard configuration.")
parser.add_argument("-key","--public-key", required=True, help="The user's public key.")
parser.add_argument("-ip","--allowed-ips", required=True, help="The allowed IP addresses for the user.")
parser.add_argument("-A","--action", required=True, help="Define you action if you want to remove the user or add user")


# Parse command-line arguments
args = parser.parse_args()
wgconf = "/etc/wireguard/wg0.conf"

# Extract the values from command-line arguments
public_key = args.public_key
allowed_ips = args.allowed_ips

hostname = node()

def addUser(public_key, allowed_ips):
        result = {}

        checks = wgvalidation.check_string_in_file(wgconf, public_key)
        ipcks = wgvalidation.check_string_in_file(wgconf, allowed_ips)
        if checks == "false" :
                if ipcks == "false":       
                        # wgvalidation.execute_backup_script()
                        command = f"/usr/bin/wg set wg0 peer {public_key} allowed-ips '{allowed_ips}'"

                        try:
                                subprocess.run(command, shell=True, check=True)
                        except subprocess.CalledProcessError as e:
                                print(f"Error: {e}")
                        wgvalidation.restart_wg()  
                        # append_key_to_file(wgconf, content)

                        output = {"Host": hostname ,"message":"User creation is successfull","public_key":public_key,"IP address":allowed_ips,"success": True}
                        result = output
                        return result
                else:
                        output = {"Host": hostname,"message":"User IP Address alredy exists, Use different one","success": False}
                        result = output
                        return result
        else:
                output = {"Host": hostname,"message":"user public key already exists.","success": False}
                result = output
                return result              


def removeuser(public_key, allowed_ips):
        result = {}
        keyCheck = wgvalidation.check_string_in_file(wgconf, public_key)
        IPCheck = wgvalidation.check_string_in_file(wgconf, allowed_ips)
        if keyCheck == "true":
               if IPCheck == "true":
                        # wgvalidation.execute_backup_script()
                        command = f"/usr/bin/wg set wg0 peer {public_key} remove allowed-ips '{allowed_ips}/32'"  
                        subprocess.run(command, shell=True, check=True)
                        wgvalidation.restart_wg()
                        output = {"Host": hostname,"message":"User Removed SuccessFully","public_key":public_key,"IP address":allowed_ips,"success": True}
                        result = output
                        return result

               else:
                      output = {"Host": hostname,"message":"User IP address doesn't exists..","success": False}
                      result = output
                      return result
        else:
                output = {"Host": hostname,"message":"User Public Key doesn't exists..","success": False}
                result = output
                return result




if __name__ == '__main__':
        if args.action == "add":
             output = addUser(public_key, allowed_ips)
             print(output)

        elif args.action == "remove":
               output = removeuser(public_key, allowed_ips)
               print(output)
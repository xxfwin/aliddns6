import subprocess

import re

   

def get_Local_ipv6_address():

    """

    This function will return your local machine's ipv6 address if it exits.

    If the local machine doesn't have a ipv6 address,then this function return None.

    This function use subprocess to execute command "ipconfig", then get the output

    and use regex to parse it ,trying to  find ipv6 address.

    """

    # run ifconfig
    getIPV6_process = subprocess.Popen("ifconfig", stdout = subprocess.PIPE)

    output = (getIPV6_process.stdout.read())
    
    # regex match ipv6_pattern
    ipv6_pattern='(([a-f0-9]{1,4}:){7}[a-f0-9]{1,4})'

    m = re.search(ipv6_pattern, str(output))

    if m is not None:

        return m.group()

    else:

        return None

 
if __name__ == '__main__':

    print(get_Local_ipv6_address())

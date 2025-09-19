import argparse
from ssh_honeypot import honeypot


if __name__ == "__main__":
    parser= argparse.ArgumentParser()
    parser.add_argument('-a','--address',type=str,required=True)
    parser.add_argument('-p','--port',type=int,required=True)
    parser.add_argument('-u','--username',type=str)
    parser.add_argument('-pw','--password',type=str)
    
    parser.add_argument('-s','--ssh',action='store_true')
    parser.add_argument('-w','--web',action='store_true')
    
    args=parser.parse_args()
    try:
        if args.ssh:
            print("[-] Running SSH Honeypot...")
            honeypot(args.username,args.password,args.port,args.address)
        elif args.web:
            print("[-] Running HTTP WordPress Honeypot...")
            pass
        else:
            print("[-] Please specify a honeypot type: --ssh or --web")
    except:
        print("\n...Exiting Honeypot...\n")
            
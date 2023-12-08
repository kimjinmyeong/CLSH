import argparse
import os
import subprocess
import sys
from typing import Tuple

SSH_PASSWORD = "ubuntu"


def parse_args() -> Tuple[dict, str]:
    """
    Parse command-line arguments and separate commands

    :return: arguments, commands
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h")
    parser.add_argument("--hostfile")
    parser.add_argument("-i", action="store_true")
    parsed = parser.parse_known_args()
    return vars(parsed[0]), " ".join(parsed[1])


def get_hosts(args: dict) -> list:
    """
    Get a list of hosts based on the provided arguments

    :param args:
    :return: hosts
    """
    if args["h"]:
        hosts = args["h"].split(",")
        return hosts
    elif args["hostfile"]:
        path = args["hostfile"]
        with open(path) as file:
            hosts = [line.rstrip() for line in file]
            return hosts
    elif os.environ.get("CLSH_HOSTS"):
        print("Note: use CLSH_HOSTS environment")
        hosts = os.environ.get("CLSH_HOSTS").split(":")
        return hosts
    elif os.environ.get("CLSH_HOSTFILE"):
        path = os.environ.get("CLSH_HOSTFILE")
        print(f"Note: use hostfile ‘{path}’ (CLSH_HOSTFILE env)")
        with open(path) as file:
            hosts = [line.rstrip() for line in file]
            return hosts
    elif os.path.exists(".hostfile"):
        print("Note: use hostfile ‘.hostfile’ (default)")
        with open(".hostfile") as file:
            hosts = [line.rstrip() for line in file]
            return hosts
    else:
        print("--hostfile option was not provided.")
        sys.exit()


def connect_ssh(hosts: list) -> dict:
    """
    Connect to SSH on the specified hosts and get subprocesses

    :param hosts:
    :return: subprocesses
    """
    process_pool = dict()
    for host in hosts:
        ssh_process = subprocess.Popen(
            ["sshpass", "-p", SSH_PASSWORD, "ssh", "-o", "StrictHostKeyChecking=no", host, "-l", "ubuntu"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        process_pool[host] = ssh_process
    return process_pool


def execute_command(subprocesses: dict, command: str, is_interactive: bool = False):
    """
    Execute the specified command on remote hosts

    :param is_interactive:
    :param subprocesses:
    :param command:
    """
    if is_interactive:
        for host, subproc in subprocesses.items():
            subproc.stdin.write(command + "\n")
            subproc.stdin.flush()  # Ensure the data is sent to the subprocess
            response = subproc.stdout.readline()
            print(f"{host}: {response}", end="")
    else:
        for host, subproc in subprocesses.items():
            response, error = subproc.communicate(command)
            print(f"{host}: {response}", end="")


def connect_node(hosts: list) -> None:
    """
    Connect to a specific node using SSH and enter interactive mode.
    This interactive mode requires entering the SSH password.
    
    :param hosts:
    :return:
    """
    print("Enter the node you want to connect to")
    print(hosts)
    target_node = input(">>")
    if target_node not in hosts:
        print("Incorrect Input!")
        return
    
    print("Enter ‘quit’ or 'exit' to leave this interactive mode")
    command = input(f"{target_node}> ")
    if command == "quit" or command == "exit":
        return 
        
    ssh_process = subprocess.Popen(
        ["ssh", "-o", "StrictHostKeyChecking=no", target_node, "-l", "ubuntu"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    
    # After entering the SSH password, execute command and enter while loop
    ssh_process.stdin.write(command + "\n")
    ssh_process.stdin.flush()  # Ensure the data is sent to the subprocess
    response = ssh_process.stdout.readline()
    print(f"{target_node}: {response}", end="")
    
    while True:
        command = input(f"{target_node}> ")
        if command == "quit" or command == "exit":
            break
        ssh_process.stdin.write(command + "\n")
        ssh_process.stdin.flush()  # Ensure the data is sent to the subprocess

        response = ssh_process.stdout.readline()
        print(f"{target_node}: {response}", end="")
    ssh_process.terminate()


def activate_interactive(subprocesses: dict):
    """
    Activate interactive mode.
    Interactive mode allows continuous execution of commands on the remote shell
    without disconnecting, providing real-time command execution and output.

    :param subprocesses:
    :return:
    """
    hosts = [host for host, _ in subprocesses.items()]
    print("Activate interactive mode !")
    print("Enter ‘quit’ or 'exit' to leave this interactive mode")
    print(f"Connected nodes: {', '.join(hosts)}")

    # Enter the internal shell.
    while True:
        command = input("clsh> ")
        if command == "quit" or command == "exit":
            break

        print("------------------------")
        if command.startswith("!"):
            local_process = subprocess.run(
                command[1:],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                universal_newlines=True,
            )
            print(f"LOCAL: {local_process.stdout}", end="")
        else:
            execute_command(subprocesses, command, True)
            print()


def terminate_all_subprocesses(subprocesses: dict):
    for host, subproc in subprocesses.items():
        subproc.terminate()


if __name__ == "__main__":
    # Parse command-line arguments and separate command
    args, command = parse_args()
    # Get a list of hosts based on the provided arguments
    hosts: list = get_hosts(args)

    # If no command is provided, activate interactive mode.
    if not command:
        if args["i"]:
            connect_node(hosts)
            sys.exit()
        else:
            subprocesses: dict = connect_ssh(hosts)
            activate_interactive(subprocesses)
    # Otherwise, execute the specified commands on remote hosts
    else:
        subprocesses: dict = connect_ssh(hosts)
        execute_command(subprocesses, command)

    terminate_all_subprocesses(subprocesses)

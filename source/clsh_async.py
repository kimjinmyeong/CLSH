import argparse
import asyncio
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


async def connect_ssh(hosts: list) -> dict:
    """
    Connect to SSH on the specified hosts and get subprocesses

    :param hosts:
    :return: subprocesses
    """
    process_pool = dict() 
    for host in hosts:
        ssh_process = await asyncio.create_subprocess_shell(
            " ".join(["sshpass", "-p", SSH_PASSWORD, "ssh", "-o", "StrictHostKeyChecking=no", host, "-l", "ubuntu"]),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        process_pool[host] = ssh_process
    return process_pool


async def execute_command(subprocesses, command):
    """
    Execute the specified command on remote hosts

    :param subprocesses:
    :param command:
    """
    for host, subproc in subprocesses.items():
        response, error = await subproc.communicate(command.encode())
        print(f"{host}: {response.decode()}", end="")


async def connect_node(hosts: list) -> None:
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

    while True:
        command = input(f"{target_node}> ")
        if command == "quit" or command == "exit":
            break
            
        ssh_process = await asyncio.create_subprocess_shell(
            " ".join(["sshpass", "-p", SSH_PASSWORD,
                      "ssh", "-o", "StrictHostKeyChecking=no", target_node, "-l", "ubuntu"]),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        response, error = await ssh_process.communicate(command.encode())
        print(f"{response.decode()}", end="")


async def activate_interactive(hosts):
    """
    Activate interactive mode.
    Interactive mode allows continuous execution of commands on the remote shell
    without disconnecting, providing real-time command execution and output.

    :param hosts:
    :return:
    """
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
            local_process = await asyncio.create_subprocess_shell(
                " ".join(command[1:]),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            print(f"LOCAL: {local_process.stdout}", end="")
        else:
            subprocesses = await connect_ssh(hosts) 
            await execute_command(subprocesses, command)
            print()


# async def terminate_all_subprocesses(subprocesses: dict):
#     for host, subproc in subprocesses.items():
#         await subproc.terminate()


async def main():
    # Parse command-line arguments and separate command
    args, command = parse_args()
    # Get a list of hosts based on the provided arguments
    hosts: list = get_hosts(args)

    # If no command is provided, activate interactive mode.
    if not command:
        if args["i"]:
            await connect_node(hosts)
            sys.exit()
        else:
            await activate_interactive(hosts)
    # Otherwise, execute the specified commands on remote hosts
    else:
        subprocesses = await connect_ssh(hosts)
        await execute_command(subprocesses, command)

    # await terminate_all_subprocesses(subprocesses)


if __name__ == "__main__":
    asyncio.run(main())

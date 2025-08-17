#!/usr/bin/env python3
import argparse
import os
import subprocess

supported_versions_to_bytes = {
    "8": [
        [b"\x84\xc0\x0f\x85\x7c\x1d\x00\x00", b"\x84\xc0\x0f\x84\x7c\x1d\x00\x00"],  # "certificate signed by unknown authority"
        [b"\x84\xc9\x0f\x84\xc0\x01\x00\x00", b"\x84\xc9\x0f\x85\xc0\x01\x00\x00"],  # "handshake did not verify certificate chain"
    ],
    "11": [[b"\x00\x0f\x85\xb3\x04\x00\x00",         b"\x00\x0f\x84\xb3\x04\x00\x00"]],
    "12": [[b"\x00\x00\x0f\x85\x43\x05\x00\x00", b"\x00\x00\x0f\x84\x43\x05\x00\x00"]],
    "13": [[b"\x00\x00\x0f\x85\x32\x05\x00\x00", b"\x00\x00\x0f\x84\x32\x05\x00\x00"]],
    "14": [[b"\x00\x00\x0f\x85\x48\x05\x00\x00", b"\x00\x00\x0f\x84\x48\x05\x00\x00"]],
    "15": [[b"\x00\x00\x0f\x85\x3a\x06\x00\x00", b"\x00\x00\x0f\x84\x3a\x06\x00\x00"]],
    "16": [[b"\x00\x00\x0f\x85\x5a\x06\x00\x00", b"\x00\x00\x0f\x84\x5a\x06\x00\x00"]],
    "17": [[b"\x00\x00\x0f\x85\x7f\x01\x00\x00", b"\x00\x00\x0f\x84\x7f\x01\x00\x00"]],
    "18": [[b"\x00\x00\x0f\x85\x7c\x01\x00\x00", b"\x00\x00\x0f\x84\x7c\x01\x00\x00"]],
    "19": [[b"\x00\x00\x0f\x85\x7b\x01\x00\x00", b"\x00\x00\x0f\x84\x7b\x01\x00\x00"]],
    "20": [[b"\x00\x00\x0f\x85\x84\x01\x00\x00", b"\x00\x00\x0f\x84\x84\x01\x00\x00"]],
    "21": [[b"\x00\x00\x0f\x85\x82\x01\x00\x00", b"\x00\x00\x0f\x84\x82\x01\x00\x00"]],
    "22": [[b"\x00\x00\x0f\x85\x82\x01\x00\x00", b"\x00\x00\x0f\x84\x82\x01\x00\x00"]],
    "23": [[b"\x00\x00\x0f\x85\x7e\x01\x00\x00", b"\x00\x00\x0f\x84\x7e\x01\x00\x00"]],
    "24": [[b"\x00\x00\x0f\x85\x7e\x01\x00\x00", b"\x00\x00\x0f\x84\x7e\x01\x00\x00"]],
}


def replace_file_bytes(file_path, old_bytes, new_bytes, print_not_found=True):
    old_bytes_str = ' '.join(f'{b:02X}' for b in old_bytes)
    new_bytes_str = ' '.join(f'{b:02X}' for b in new_bytes)

    with open(file_path, 'rb') as f:
        data = f.read()
        position = data.find(old_bytes)

    if position == -1:
        if print_not_found:
            print(f"[!] Error: unable to find TLS \"InsecureSkipVerify\" bytes to patch! (looked for: \"{old_bytes_str}\")")
        return

    hex_position = hex(position)
    print(f"[+] TLS \"InsecureSkipVerify\" check found at offset: {position} ({hex_position})")

    with open(file_path, 'rb+') as file:
        file.seek(position)
        existing_bytes = file.read(len(old_bytes))

        if existing_bytes == old_bytes:
            file.seek(position)
            file.write(new_bytes)
            print(f"[+] TLS \"InsecureSkipVerify\" patched \"{old_bytes_str}\" -> \"{new_bytes_str}\"")
            return True


def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()


def get_go_bin_version(filename):
    output = run_command(f"strings {filename} | grep '^go1' | head -n 1")
    if "" == output:
        output = run_command(f"strings {filename} | grep 'Go cmd/compile'  | head -n 1 | cut -d' ' -f 3")
        if "" == output:
            output = run_command(f"strings {filename} | grep -Eo 'go[0-9]+\\.[0-9]+(\\.[0-9]+)?' | head -n 1")

    if output:
        output = output.replace("go", "")
        parts = output.split(".")
        output = f"{parts[0]}.{parts[1]}"

    return output


def get_args():
    parser = argparse.ArgumentParser(description='Get a filename and patches its SSL verification check')
    parser.add_argument("-a", "--about", help='About this app', action='store_true')
    parser.add_argument("-n", "--nologo", help='Don\'t print the logo', action='store_true')

    parser.add_argument("-f", "--filename", help='File to patch')
    parser.add_argument("-g", "--get-version", help='Only print the detected Golang version', action='store_true')
    parser.add_argument("-v", "--version", help='Input version of Golang app')

    parser.add_argument("-s", "--singlepatch", help='Patch only the first occurrence', action='store_true')
    parser.add_argument("-u", "--unpatch", help='Attempt to undo patching and restore original bytes', action='store_true')

    return parser.parse_args()


def main():
    args = get_args()

    if not args.nologo:
        print()
        print(" ██████╗  ██████╗     ██████╗ ██╗   ██╗██████╗ ██████╗ ██╗███╗   ██╗ ██████╗ ")
        print("██╔════╝ ██╔═══██╗    ██╔══██╗██║   ██║██╔══██╗██╔══██╗██║████╗  ██║██╔════╝ ")
        print("██║  ███╗██║   ██║    ██████╔╝██║   ██║██████╔╝██████╔╝██║██╔██╗ ██║██║  ███╗")
        print("██║   ██║██║   ██║    ██╔══██╗██║   ██║██╔══██╗██╔═══╝ ██║██║╚██╗██║██║   ██║")
        print("╚██████╔╝╚██████╔╝    ██████╔╝╚██████╔╝██║  ██║██║     ██║██║ ╚████║╚██████╔╝")
        print(" ╚═════╝  ╚═════╝     ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═════╝ ")
        print("                                                                           v1.2")
        print()

    if args.about:
        print("[*] Created by CyberArk: https://www.cyberark.com/resources/all-blog-posts/how-to-bypass-golang-ssl-verification")
        print("[*] Updated by Hypn: https://x.com/hypninfosec")
        print()
        return

    if not args.filename:
        print("[!] Error: no filename specified! Use `-f {filename}`")
        print()
        return

    print(f"[*] Filename: \"{args.filename}\"")

    if not os.path.isfile(args.filename):
        print(f"[!] Filename does not exist or is not a readable file!")
        print()
        return

    version = get_go_bin_version(args.filename)
    if version:
        print(f"[*] Go version detected: {version}")

        # if the user only wanted to see the version
        if args.get_version:
            print()
            return
    else:
        print(f"[!] Error determining Go version!")
        return

    if args.version:
        print(f"[!] Overriding detected Go version {version} with specified version: {args.version}")
        version = args.version

    minor = version
    if "." in version:
        minor = version.split(".")[1]

    supported = supported_versions_to_bytes.get(minor, [])
    if not supported:
        print(f"[!] Error: Golang version {version} is not supported!")
        return

    for patterns in supported:
        if args.unpatch:
            print(f"[!] Attempting to UNDO patch(es)!")
            new_bytes = patterns[0]
            old_bytes = patterns[1]
        else:
            old_bytes = patterns[0]
            new_bytes = patterns[1]

        patched = False
        while True:
            if patched:
                print_not_found = False
            else:
                print_not_found = True

            patched = replace_file_bytes(args.filename, old_bytes, new_bytes, print_not_found)
            if args.singlepatch or not patched:
                print(f"[*] Done!")
                break

    print()


if "__main__" == __name__:
    main()

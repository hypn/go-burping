# Go Burping

A Python script for patching Go binaries, to bypass SSL cert verification and facilitate HTTPS traffic proxying and interception.

The code comes from ["How to Bypass Golang SSL Verification" by Michael Pasternak](https://www.cyberark.com/resources/all-blog-posts/how-to-bypass-golang-ssl-verification) on the CyberArk blog, and has been updated and bytes for Go > 21 added.

## Basic Usage:

**NOTE: This will modify your file, it's recommended to make a backup or copy of it first**

Download or git clone the python script in this repo and run it with Python3, using `-f` to specify your Go binary to be patched. Eg:

```
python goburping.py -f test-bin

 ██████╗  ██████╗     ██████╗ ██╗   ██╗██████╗ ██████╗ ██╗███╗   ██╗ ██████╗
██╔════╝ ██╔═══██╗    ██╔══██╗██║   ██║██╔══██╗██╔══██╗██║████╗  ██║██╔════╝
██║  ███╗██║   ██║    ██████╔╝██║   ██║██████╔╝██████╔╝██║██╔██╗ ██║██║  ███╗
██║   ██║██║   ██║    ██╔══██╗██║   ██║██╔══██╗██╔═══╝ ██║██║╚██╗██║██║   ██║
╚██████╔╝╚██████╔╝    ██████╔╝╚██████╔╝██║  ██║██║     ██║██║ ╚████║╚██████╔╝
 ╚═════╝  ╚═════╝     ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═════╝
                                                                           v1.2

[*] Filename: "test-bin"
[*] Go version detected: 1.23
[+] TLS "InsecureSkipVerify" check found at offset: 1852356 (0x1c43c4)
[+] TLS "InsecureSkipVerify" patched "00 00 0F 85 7E 01 00 00" -> "00 00 0F 84 7E 01 00 00"
[+] TLS "InsecureSkipVerify" check found at offset: 1887013 (0x1ccb25)
[+] TLS "InsecureSkipVerify" patched "00 00 0F 85 7E 01 00 00" -> "00 00 0F 84 7E 01 00 00"
[+] TLS "InsecureSkipVerify" check found at offset: 1888869 (0x1cd265)
[+] TLS "InsecureSkipVerify" patched "00 00 0F 85 7E 01 00 00" -> "00 00 0F 84 7E 01 00 00"
[*] Done!
```

**Before Patching:**
```
HTTPS_PROXY=http://192.168.0.100:8080 ./test-bin
2025/08/04 08:03:02 Get "https://ipinfo.io/": tls: failed to verify certificate: x509: certificate signed by unknown authority
```

**After Patching:***
```
HTTPS_PROXY=http://192.168.0.100:8080 ./test-bin
2025/08/04 08:03:25 {
  "ip": "REDACTED",
  [...]
  "readme": "https://ipinfo.io/missingauth"
}
```


Run the script with `-h` to see the other options available:
```
python goburping.py -h
usage: goburping.py [-h] [-a] [-n] [-f FILENAME] [-g] [-v VERSION] [-s] [-u]

Get a filename and patches its SSL verification check

options:
  -h, --help            show this help message and exit
  -a, --about           About this app
  -n, --nologo          Don't print the logo
  -f FILENAME, --filename FILENAME
                        File to patch
  -g, --get-version     Only print the detected Golang version
  -v VERSION, --version VERSION
                        Input version of Golang app
  -s, --singlepatch     Patch only the first occurrence
  -u, --unpatch         Attempt to undo patching and restore original bytes
```

## Other:

A blog post should follow in the near future, on [https://hypn.za.net/](https://hypn.za.net/), about using "[mise](https://mise.jdx.dev/lang/go.html)" to compile code with multiple versions of Go and using Ghidra to find these bytes for new Go versions. See the [test-app](test-app) directory for example app provided by CyberArk to help with this.


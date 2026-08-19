# Tor SMTP Mail Client

A Python desktop SMTP mail client built with **Tkinter**, **smtplib**,
and **PySocks**. It can optionally attach documents and route its SMTP
socket connection through a local **Tor SOCKS5 proxy**.

> **Purpose:** This project is primarily an educational
> cybersecurity/networking project for learning SMTP, TLS, SOCKS5
> proxying, Tor integration, MIME email construction, GUI programming,
> and privacy limitations.

## Features

-   Tkinter graphical interface
-   Gmail, Outlook, Yahoo, and custom SMTP provider selection
-   Automatic SMTP server/port population for supported providers
-   STARTTLS support
-   SMTP authentication
-   Optional document attachments
-   File-selection dialog
-   Add/remove attachment controls
-   SOCKS5 routing through Tor
-   Remote DNS requested through the SOCKS5 proxy
-   Basic validation and error handling
-   Status reporting through the GUI

## How the Project Works

The network path is intended to be:

``` text
Tkinter GUI
    |
    v
Python SMTP client (smtplib)
    |
    v
PySocks socket
    |
    v
SOCKS5 proxy
127.0.0.1:9050
    |
    v
Tor network
    |
    v
SMTP server
    |
    v
Recipient's mail infrastructure
```

The project replaces Python's normal `socket.socket` implementation with
`socks.socksocket`. Consequently, connections created by libraries using
Python sockets can be sent through the configured SOCKS5 proxy.

### Why Tor is needed

The application itself is an SMTP client. SMTP normally establishes a
network connection directly to the configured mail server. Tor provides
an additional network-routing layer between the application and the
destination.

In this project:

1.  Tor runs locally.
2.  Tor exposes a SOCKS5 listener, configured here as `127.0.0.1:9050`.
3.  PySocks sends the application's connection through that listener.
4.  Tor routes the connection through the Tor network.
5.  The SMTP session is then established with the mail provider.
6.  STARTTLS protects the SMTP session between the client and SMTP
    server.

**Tor and TLS are not the same thing.**

-   **Tor:** provides a privacy-oriented network path.
-   **TLS:** encrypts the SMTP session between the client and SMTP
    server.
-   **SMTP authentication:** identifies/authenticates the account to the
    mail provider.

Tor therefore does not replace TLS, and TLS does not replace Tor.

## Important Privacy Clarification

This project should **not** be described as an anonymous email system.

Using Tor does not remove all identifying information from email.

Potentially identifying information includes:

-   The SMTP account used to authenticate
-   The sender address
-   Email headers and metadata
-   The recipient address
-   Mail-provider logs
-   Account activity associated with the sender
-   Message content
-   Attachment contents
-   Information voluntarily included in the email
-   Endpoint compromise or malware
-   Application or configuration mistakes

Tor can change the network path visible to the destination, but it
cannot erase the identity associated with an SMTP account.

## Firefox Relay

Users who want to keep their normal email address private when signing
up for websites can use **Firefox Relay**.

Firefox Relay creates email masks that forward messages to the user's
real mailbox without exposing the real address to the sender. Mozilla
describes Relay as a way to protect the real email address from
companies and reduce spam.

Official service:

https://relay.firefox.com/

Mozilla documentation:

https://support.mozilla.org/en-US/kb/create-email-mask-through-firefox-relay

A useful workflow can be:

``` text
Website / service
       |
       v
Firefox Relay email mask
       |
       v
Real email inbox
```

This is different from Tor.

-   **Firefox Relay:** masks the user's email address from third
    parties.
-   **Tor:** provides a privacy-oriented network route.
-   **TLS:** protects the SMTP connection while in transit.

### Important Relay limitation

Firefox Relay is not appropriate for every type of email. Mozilla
specifically recommends using a real address for situations requiring
identity verification or important messages, and notes limitations
around attachment forwarding. Relay currently has a 10 MB forwarding
limit for emails with attachments.

Do not treat Relay as a replacement for a normal email account.

## Installation

### 1. Clone the project

``` bash
git clone <YOUR_REPOSITORY_URL>
cd <PROJECT_DIRECTORY>
```

### 2. Install Python dependencies

The project requires:

``` text
PySocks
```

Install it with:

``` bash
python -m pip install PySocks
```

Tkinter is normally supplied by the operating system rather than
installed through pip.

## Installing Tor

This project needs a **running Tor daemon with a SOCKS5 listener**. Tor
Browser and the Tor daemon are related but are not interchangeable for
this application's `127.0.0.1:9050` configuration.

Always prefer the Tor Project's official documentation and downloads.

Official Tor downloads:

https://www.torproject.org/download/

### Arch Linux

Install Tor:

``` bash
sudo pacman -Syu tor
```

Enable and start the service:

``` bash
sudo systemctl enable --now tor
```

Check its status:

``` bash
systemctl status tor
```

Check whether something is listening on port 9050:

``` bash
ss -lntp | grep 9050
```

The Tor Project documents the Arch package as `tor` and uses systemd to
enable/start the service.

### Debian / Ubuntu

The Tor Project recommends using its official package repository rather
than relying on old distribution packages.

Follow the current Tor Project repository instructions first, then
install:

``` bash
sudo apt install tor
```

Start the service:

``` bash
sudo systemctl enable --now tor
```

Check:

``` bash
systemctl status tor
```

The repository instructions can change between Debian/Ubuntu releases,
so use the current official Tor documentation rather than copying an old
repository configuration into a new system.

### Fedora

Configure the current Tor Project Fedora repository according to the
official documentation, then install:

``` bash
sudo dnf install tor
```

Start it:

``` bash
sudo systemctl enable --now tor
```

Check:

``` bash
systemctl status tor
```

### macOS

Using Homebrew:

``` bash
brew install tor
```

Then start Tor according to Homebrew's service management:

``` bash
brew services start tor
```

Check the service:

``` bash
brew services list
```

The Tor Project also documents installation through MacPorts:

``` bash
sudo port install tor
```

### Windows

For Windows, the Tor Project provides a **Windows Expert Bundle** for
running the Tor daemon. Download it from the official Tor Project
sources rather than downloading `tor.exe` from an unknown third-party
website.

Tor Project Windows documentation:

https://community.torproject.org/relay/setup/guard/windows/

After installing/configuring the daemon, make sure the Tor configuration
provides a local SOCKS listener on:

``` text
127.0.0.1:9050
```

Then verify the listener from PowerShell:

``` powershell
Get-NetTCPConnection -LocalPort 9050
```

If you are using Tor Browser instead of a standalone Tor daemon, do not
assume that port `9050` is available. Verify the SOCKS listener and port
actually exposed by your Tor installation.

### FreeBSD

The Tor Project documents:

``` bash
sudo pkg install tor
```

Then configure/start the service according to the FreeBSD service
system.

### OpenBSD

The Tor Project documents:

``` bash
sudo pkg_add tor
```

Then configure/start Tor according to OpenBSD's service conventions.

## Verify Tor Before Running the Application

Before launching this project, verify that Tor is actually running.

### Linux

``` bash
ss -lntp | grep 9050
```

You should see a local listener associated with Tor.

You can also inspect the service:

``` bash
systemctl status tor
```

### macOS

``` bash
lsof -nP -iTCP:9050 -sTCP:LISTEN
```

### Windows PowerShell

``` powershell
Get-NetTCPConnection -LocalPort 9050
```

If nothing is listening on `127.0.0.1:9050`, this application will not
be able to connect through the configured SOCKS5 proxy.

## Running the Application

Run:

``` bash
python smtp_client.py
```

or, depending on your Python installation:

``` bash
python3 smtp_client.py
```

The GUI should open.

### Basic workflow

1.  Select an SMTP provider.
2.  Confirm the SMTP server and port.
3.  Enter the sender email.
4.  Enter the SMTP password/app password.
5.  Enter the recipient.
6.  Enter a subject.
7.  Write the message.
8.  Optionally click **Add Attachment**.
9.  Select a document.
10. Click **SEND EMAIL**.

The attachment is optional. If no attachment is selected, only the email
body is sent.

## SMTP Credentials

Do not commit passwords into Git.

Do not put passwords directly into source code.

For real deployments, consider using:

-   Environment variables
-   OS credential stores
-   A dedicated secrets manager
-   Provider-specific app passwords where required

For example, do not commit:

``` text
password = "MyRealPassword123"
```

to a public repository.

Add secret files to `.gitignore`.

## Gmail and App Passwords

Some providers require an **app password** or another authentication
mechanism instead of the normal account password.

The exact requirements depend on the provider and account configuration.

The GUI therefore labels the credential field:

``` text
SMTP Password / App Password
```

Do not disable account security features merely to make the program
work.

## Security Model

The application has several security layers:

``` text
Application
    |
    +-- MIME email construction
    |
    +-- SMTP authentication
    |
    +-- STARTTLS
    |
    +-- SOCKS5
    |
    +-- Tor
    |
    +-- SMTP infrastructure
```

Each layer has a different purpose.

### MIME

Packages the message body and optional attachment into an email
structure.

### SMTP authentication

Authenticates the account to the mail provider.

### STARTTLS

Encrypts the SMTP session after the initial connection and protects
credentials/content during the TLS-protected portion of the session.

### SOCKS5

Provides a proxy interface between the Python application and Tor.

### Tor

Provides the privacy-oriented network-routing layer.

## Weaknesses and Limitations

This project has significant limitations.

### 1. It is not an anonymous email service

The SMTP provider still knows which account authenticated.

Using an identifiable account can directly associate the message with
that account.

### 2. Tor does not protect the endpoint

If the computer is compromised, Tor cannot protect the application from:

-   Malware
-   Keyloggers
-   Credential theft
-   Screen capture
-   Local file theft
-   Browser/session compromise

### 3. SMTP providers may reject Tor connections

Some providers restrict or challenge connections originating from Tor
exit nodes.

Possible results include:

``` text
Connection refused
Authentication failed
Account verification required
Temporary block
Captcha / security challenge
```

These are provider-side controls.

### 4. Tor does not encrypt the entire email ecosystem

The project uses STARTTLS for the client-to-SMTP connection, but email
is not automatically end-to-end encrypted between sender and recipient.

For true message-level confidentiality, technologies such as OpenPGP or
S/MIME are separate considerations.

### 5. Email metadata remains important

Even when message contents are protected in transit, email systems still
process metadata such as:

-   Sender
-   Recipient
-   Time
-   Message size
-   Routing information

### 6. Attachments can leak information

A document may contain:

-   Author metadata
-   Creation timestamps
-   Editing software information
-   Embedded usernames
-   GPS metadata in images
-   Internal paths
-   Hidden document properties

Tor does not remove metadata from a file.

### 7. DNS protection depends on correct proxy configuration

The program requests remote DNS resolution using:

``` python
rdns=True
```

However, privacy depends on the complete system/application
configuration. Do not assume that changing one socket setting
automatically prevents every possible information leak.

### 8. Monkey-patching sockets has risks

This line:

``` python
socket.socket = socks.socksocket
```

changes the socket implementation globally within the Python process.

That can cause unexpected behavior in libraries that were not designed
to operate through a SOCKS proxy.

A more robust production design would explicitly configure the network
client instead of globally replacing the socket class.

### 9. No attachment encryption

The attachment is only packaged as a MIME attachment.

It is not independently encrypted.

If the document contains sensitive information, consider encrypting the
document before attaching it.

### 10. No certificate pinning

The program uses normal TLS certificate validation provided by Python's
TLS stack. It does not implement certificate pinning.

### 11. Credentials are entered into the application

The GUI receives the SMTP credential. A compromised local machine could
potentially capture it.

## Security Improvements for Future Versions

Possible future improvements include:

-   Environment-variable credential support
-   OS keyring integration
-   Explicit SOCKS proxy support rather than global socket
    monkey-patching
-   Better MIME type detection
-   Attachment size limits
-   Attachment hashing
-   Optional client-side attachment encryption
-   OpenPGP support
-   Certificate validation diagnostics
-   Connection testing
-   Tor connectivity testing
-   Automatic Tor status detection
-   Configurable SOCKS host/port
-   Secure logging without credentials
-   Password field clearing after use
-   Session timeout
-   Multiple recipients
-   CC/BCC support
-   HTML email support
-   Email drafts
-   SMTP connection diagnostics

## Project Structure

A recommended structure is:

``` text
tor-smtp-client/
|
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
|
├── src/
│   ├── gui.py
│   ├── smtp_client.py
│   ├── attachment.py
│   ├── tor_proxy.py
│   └── config.py
|
└── tests/
    ├── test_attachment.py
    ├── test_smtp.py
    └── test_tor_proxy.py
```

The current single-file version is useful for learning. Splitting the
project into modules is recommended as the project grows.

## Educational Purpose

This project demonstrates several cybersecurity concepts in one
application:

### Networking

-   TCP sockets
-   SOCKS5
-   Proxying
-   DNS resolution
-   Network routing

### Email security

-   SMTP
-   STARTTLS
-   Authentication
-   MIME
-   Attachments

### Privacy

-   Tor
-   Network metadata
-   Email identity
-   Email masking
-   Endpoint security

### Python

-   Object-oriented/library APIs
-   Exception handling
-   File I/O
-   GUI programming
-   Networking
-   MIME construction

## Ethical Use

Use this project only for legitimate purposes.

Do not use it to:

-   Evade lawful security controls
-   Harass or impersonate people
-   Send spam
-   Send malicious attachments
-   Bypass provider restrictions
-   Conduct phishing
-   Conceal criminal activity

The intended use is experimentation, privacy education, networking
education, and authorized security research.

## Troubleshooting

### `Connection refused`

Check whether Tor is running:

``` bash
systemctl status tor
```

Then check port 9050:

``` bash
ss -lntp | grep 9050
```

### SOCKS connection fails

Verify:

``` text
SOCKS host: 127.0.0.1
SOCKS port: 9050
```

If your Tor installation uses another port, change the application
configuration accordingly.

### SMTP authentication fails

Check:

-   SMTP server
-   SMTP port
-   Username
-   Password/app password
-   Provider authentication requirements
-   Whether the provider permits the connection

### STARTTLS fails

Verify that the SMTP server supports STARTTLS on the selected port and
that the provider's current SMTP requirements match the application's
configuration.

### Attachment fails

Check:

-   File exists
-   File is readable
-   File path is correct
-   File size is reasonable
-   Provider attachment restrictions

## Disclaimer

This software is an educational project. It does not guarantee
anonymity, confidentiality, undetectability, or protection from
monitoring.

Tor, TLS, SMTP authentication, and Firefox Relay each solve different
privacy or security problems. They should be understood as separate
components rather than as a single anonymity mechanism.

## References

-   Tor Project: https://www.torproject.org/
-   Tor Downloads: https://www.torproject.org/download/
-   Tor installation documentation:
    https://community.torproject.org/onion-services/setup/install/
-   Tor Windows documentation:
    https://community.torproject.org/relay/setup/guard/windows/
-   Tor Arch Linux documentation:
    https://community.torproject.org/relay/setup/guard/archlinux/
-   Firefox Relay: https://relay.firefox.com/
-   Firefox Relay email masks:
    https://support.mozilla.org/en-US/kb/create-email-mask-through-firefox-relay
-   Firefox Relay FAQ: https://relay.firefox.com/faq/

## License

Choose an appropriate open-source license before publishing this
project. MIT is a common choice for educational projects, but select the
license that matches your intended use and contribution model.

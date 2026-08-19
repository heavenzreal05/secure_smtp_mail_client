import socket
import smtplib
import socks
import os
import tkinter as tk

from tkinter import ttk, filedialog, messagebox
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


# ============================================================
# 1.T OR / SOCKS5 CONFIGURATION
# ============================================================

# Tor SOCKS5 proxy
TOR_HOST = "127.0.0.1"
TOR_PORT = 9050

socks.set_default_proxy(
    socks.SOCKS5,
    TOR_HOST,
    TOR_PORT,
    rdns=True
)

#Redirect Python socket connections through PySocks
socket.socket = socks.socksocket


# ============================================================
# 2. SMTP PROVIDERS
# ============================================================

SMTP_PROVIDERS = {

    "Gmail": {
        "server": "smtp.gmail.com",
        "port": 587
    },

    "Outlook": {
        "server": "smtp-mail.outlook.com",
        "port": 587
    },

    "Yahoo": {
        "server": "smtp.mail.yahoo.com",
        "port": 587
    },

    "Custom": {
        "server": "",
        "port": 587
    }
}


# ============================================================
# 3. GLOBAL ATTACHMENT VARIABLE
# ============================================================

attachment_path = None


# ============================================================
# 4. UPDATE SMTP SERVER
# ============================================================

def update_smtp_server(event=None):

    provider = provider_combo.get()

    settings = SMTP_PROVIDERS.get(
        provider,
        SMTP_PROVIDERS["Custom"]
    )

    smtp_server_entry.delete(
        0,
        tk.END
    )

    smtp_server_entry.insert(
        0,
        settings["server"]
    )

    smtp_port_entry.delete(
        0,
        tk.END
    )

    smtp_port_entry.insert(
        0,
        settings["port"]
    )


# ============================================================
# 5. CHOOSE ATTACHMENT
# ============================================================

def choose_file():

    global attachment_path

    selected_file = filedialog.askopenfilename(

        title="Select Document",

        filetypes=[
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx"),
            ("Text files", "*.txt"),
            ("CSV files", "*.csv"),
            ("Images", "*.png *.jpg *.jpeg"),
            ("All files", "*.*")
        ]
    )

    if selected_file:

        attachment_path = selected_file

        attachment_label.config(
            text=f"Attachment: {os.path.basename(selected_file)}"
        )

        status_label.config(
            text="Attachment selected."
        )

    else:

        attachment_path = None

        attachment_label.config(
            text="Attachment: None"
        )


# ============================================================
# 6. REMOVE ATTACHMENT
# ============================================================

def remove_attachment():

    global attachment_path

    attachment_path = None

    attachment_label.config(
        text="Attachment: None"
    )

    status_label.config(
        text="Attachment removed."
    )


# ============================================================
# 7. SEND EMAIL
# ============================================================

def send_email():

    global attachment_path

    smtp_server = smtp_server_entry.get().strip()
    smtp_port = smtp_port_entry.get().strip()

    sender_email = sender_entry.get().strip()
    password = password_entry.get()

    receiver_email = receiver_entry.get().strip()

    subject = subject_entry.get().strip()

    message_body = message_text.get(
        "1.0",
        tk.END
    ).strip()


    # --------------------------------------------------------
    # Validate SMTP server
    # --------------------------------------------------------

    if not smtp_server:

        messagebox.showerror(
            "Error",
            "SMTP server is required."
        )

        return


    # --------------------------------------------------------
    # Validate SMTP port
    # --------------------------------------------------------

    try:

        smtp_port = int(smtp_port)

    except ValueError:

        messagebox.showerror(
            "Error",
            "SMTP port must be a number."
        )

        return


    # --------------------------------------------------------
    # Validate sender
    # --------------------------------------------------------

    if not sender_email:

        messagebox.showerror(
            "Error",
            "Sender email is required."
        )

        return


    # --------------------------------------------------------
    # Validate password
    # --------------------------------------------------------

    if not password:

        messagebox.showerror(
            "Error",
            "SMTP password/app password is required."
        )

        return


    # --------------------------------------------------------
    # Validate recipient
    # --------------------------------------------------------

    if not receiver_email:

        messagebox.showerror(
            "Error",
            "Recipient email is required."
        )

        return


    # --------------------------------------------------------
    # Create multipart email
    # --------------------------------------------------------

    msg = MIMEMultipart()

    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email


    # --------------------------------------------------------
    # Add message body
    # --------------------------------------------------------

    body = MIMEText(
        message_body,
        "plain"
    )

    msg.attach(body)


    # --------------------------------------------------------
    # Optional attachment
    # --------------------------------------------------------

    if attachment_path:

        if not os.path.isfile(attachment_path):

            messagebox.showerror(
                "Attachment Error",
                "The selected file does not exist."
            )

            return


        try:

            with open(
                attachment_path,
                "rb"
            ) as file:

                attachment = MIMEApplication(
                    file.read(),
                    Name=os.path.basename(
                        attachment_path
                    )
                )


            attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename=os.path.basename(
                    attachment_path
                )
            )


            msg.attach(attachment)


        except Exception as e:

            messagebox.showerror(
                "Attachment Error",
                f"Could not read attachment:\n{e}"
            )

            return


    # --------------------------------------------------------
    # Connect to SMTP server
    # --------------------------------------------------------

    server = None

    try:

        status_label.config(
            text="Connecting through Tor..."
        )

        root.update_idletasks()


        server = smtplib.SMTP(
            smtp_server,
            smtp_port,
            timeout=30
        )


        # ----------------------------------------------------
        # Identify client to SMTP server
        # ----------------------------------------------------

        server.ehlo()


        # ----------------------------------------------------
        # STARTTLS
        # ----------------------------------------------------

        status_label.config(
            text="Establishing TLS..."
        )

        root.update_idletasks()


        server.starttls()


        # EHLO again after STARTTLS
        server.ehlo()


        # ----------------------------------------------------
        # Authenticate
        # ----------------------------------------------------

        status_label.config(
            text="Authenticating..."
        )

        root.update_idletasks()


        server.login(
            sender_email,
            password
        )


        # ----------------------------------------------------
        # Send email
        # ----------------------------------------------------

        status_label.config(
            text="Sending email..."
        )

        root.update_idletasks()


        server.sendmail(
            sender_email,
            receiver_email,
            msg.as_string()
        )


        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------

        status_label.config(
            text="Email sent successfully."
        )


        messagebox.showinfo(
            "Success",
            "Email successfully sent."
        )


    except Exception as e:

        status_label.config(
            text="SMTP error."
        )


        messagebox.showerror(
            "SMTP Error",
            str(e)
        )


    finally:

        if server:

            try:

                server.quit()

            except Exception:

                pass


# ============================================================
# 8. MAIN WINDOW
# ============================================================

root = tk.Tk()

root.title(
    "Tor SMTP Mail Client"
)

root.geometry(
    "500x600"
)

root.resizable(
    False,
    False
)


# ============================================================
# 9. TITLE
# ============================================================

title_label = tk.Label(
    root,
    text="Secure SMTP Mail Client",
    font=("Arial", 16, "bold")
)

title_label.pack(
    pady=8
)


# ============================================================
# 10. TOP BUTTONS
# ============================================================

button_frame = tk.Frame(root)

button_frame.pack(
    pady=4
)


# Add attachment
choose_button = tk.Button(
    button_frame,
    text="Add Attachment",
    command=choose_file,
    width=16
)

choose_button.pack(
    side=tk.LEFT,
    padx=3
)


# Remove attachment
remove_button = tk.Button(
    button_frame,
    text="Remove Attachment",
    command=remove_attachment,
    width=16
)

remove_button.pack(
    side=tk.LEFT,
    padx=3
)


# Send email
send_button = tk.Button(
    button_frame,
    text="SEND EMAIL",
    command=send_email,
    width=16
)

send_button.pack(
    side=tk.LEFT,
    padx=3
)


# ============================================================
# 11. ATTACHMENT STATUS
# ============================================================

attachment_label = tk.Label(
    root,
    text="Attachment: None"
)

attachment_label.pack(
    pady=4
)


# ============================================================
# 12. SMTP PROVIDER
# ============================================================

tk.Label(
    root,
    text="SMTP Provider"
).pack()


provider_combo = ttk.Combobox(
    root,
    values=[
        "Gmail",
        "Outlook",
        "Yahoo",
        "Custom"
    ],
    state="readonly",
    width=52
)

provider_combo.pack(
    pady=2
)

provider_combo.set(
    "Gmail"
)

provider_combo.bind(
    "<<ComboboxSelected>>",
    update_smtp_server
)


# ============================================================
# 13. SMTP SERVER
# ============================================================

tk.Label(
    root,
    text="SMTP Server"
).pack()


smtp_server_entry = tk.Entry(
    root,
    width=55
)

smtp_server_entry.pack(
    pady=2
)

smtp_server_entry.insert(
    0,
    SMTP_PROVIDERS["Gmail"]["server"]
)


# ============================================================
# 14. SMTP PORT
# ============================================================

tk.Label(
    root,
    text="SMTP Port"
).pack()


smtp_port_entry = tk.Entry(
    root,
    width=55
)

smtp_port_entry.pack(
    pady=2
)

smtp_port_entry.insert(
    0,
    SMTP_PROVIDERS["Gmail"]["port"]
)


# ============================================================
# 15. SENDER
# ============================================================

tk.Label(
    root,
    text="Sender Email"
).pack()


sender_entry = tk.Entry(
    root,
    width=55
)

sender_entry.pack(
    pady=2
)


# ============================================================
# 16. PASSWORD
# ============================================================

tk.Label(
    root,
    text="SMTP Password / App Password"
).pack()


password_entry = tk.Entry(
    root,
    width=55,
    show="*"
)

password_entry.pack(
    pady=2
)


# ============================================================
# 17. RECIPIENT
# ============================================================

tk.Label(
    root,
    text="Recipient Email"
).pack()


receiver_entry = tk.Entry(
    root,
    width=55
)

receiver_entry.pack(
    pady=2
)


# ============================================================
# 18. SUBJECT
# ============================================================

tk.Label(
    root,
    text="Subject"
).pack()


subject_entry = tk.Entry(
    root,
    width=55
)

subject_entry.pack(
    pady=2
)


# ============================================================
# 19. MESSAGE
# ============================================================

tk.Label(
    root,
    text="Message"
).pack()


message_text = tk.Text(
    root,
    width=55,
    height=5
)

message_text.pack(
    pady=3
)


# ============================================================
# 20. STATUS
# ============================================================

status_label = tk.Label(
    root,
    text="Ready",
    font=("Arial", 9)
)

status_label.pack(
    pady=3
)


# ============================================================
# 21. START APPLICATION
# ============================================================

root.mainloop()

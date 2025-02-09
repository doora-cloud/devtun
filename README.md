Below is a complete example of a README.md file written in English:

# DevTun - SSH Port Forwarding Tool

## Overview
DevTun is a Python-based SSH port forwarding tool that enables you to easily set up and manage SSH tunnels for port forwarding. It supports multiple tunnels, real-time SSH connection monitoring, and network statistics. Configuration is handled through files stored in `~/.config/devtun/`.

## Features
- **Manage Multiple SSH Tunnels:** Easily add, edit, and delete services.
- **Real-Time Dashboard:** Monitor SSH connection status and network statistics.
- **Auto-Reconnect:** Tunnels will continuously attempt to reconnect if the SSH connection is lost.
- **Flexible SSH Configuration:** Store your SSH details in a configuration file.

## Requirements
- **Python:** Version 3.6 or higher.
- **Python Packages:**
  - [psutil](https://pypi.org/project/psutil/)
  - [rich](https://pypi.org/project/rich/)

The required packages are listed in the [`requirements.txt`](requirements.txt) file.

## Installation

### 1. Clone the Repository or Download the Source Code
If you are using Git, run the following commands:
```bash
git clone <repository URL>
cd <project-directory>
```

### 2. Create the requirements.txt File

Create a file named requirements.txt with the following content:

```text
psutil
rich
```

### 3. Install the Required Packages

Install the dependencies using pip:

```bash
pip install -r requirements.txt
```

## SSH Configuration

### First Run

When you run DevTun for the first time, you will be prompted to enter your SSH configuration details:
	•	SSH Host
	•	SSH Port (default is 22)
	•	SSH Username
	•	Path to your Private Key

These details will be saved to a configuration file located at:

```text
~/.config/devtun/config.json
```

### Updating SSH Configuration

At any time, you can update your SSH configuration by selecting option 6. Update SSH Configuration from the main menu.

## Usage

### 1. Running DevTun

To start the application, run:

```bash
python devtun.py
```

### 2. Main Menu Options

After launching the program, you will see a menu with the following options:
	•	1. Start All Services 🚀:
Starts all configured SSH tunnels. Tunnels will automatically try to reconnect if the connection is lost.
	•	2. List Services 📝:
Displays a list of all configured services.
	•	3. Add Service ➕:
Allows you to add a new service by providing:
	•	Service name
	•	Local port
	•	Remote host
	•	Remote port
	•	4. Edit Service ✏️:
Edit an existing service configuration.
	•	5. Delete Service 🗑️:
Delete a service from the configuration list.
	•	6. Update SSH Configuration 🔧:
Update your SSH configuration details.
	•	0. Exit ❌:
Exit the application.

### 3. Dashboard

Once the services are started, a dashboard will be displayed with:
	•	SSH Server Status:
Indicates if the SSH server is connected or disconnected.
	•	Network Statistics:
Real-time monitoring of bytes sent and received.
	•	Running Services Dashboard:
A table listing:
	•	Service name
	•	Inbound (local port)
	•	Outbound (remote host and port)
	•	Current status (Running/Stopped)

## Security Considerations
### Sensitive Information:

Your SSH details (such as host, username, and private key path) are stored in the configuration file at ~/.config/devtun/config.json. Ensure that this file is secure and not publicly accessible.

### Data Sharing:
Avoid sharing your configuration file or sensitive details in public repositories.

### Support & Contact

If you encounter any issues or have any questions, please contact:
	•	Email: email@example.com
	•	GitHub: Your GitHub Profile/Repository

## License

Include license details here if applicable.
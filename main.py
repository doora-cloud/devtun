import subprocess
import threading
import json
import time
import psutil
import sys
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Global variables
services = []
tunnels = {}  # Dictionary chứa các đối tượng ServiceTunnel (key có thể là index của dịch vụ)
ssh_connected = False
console = Console()

# Paths for configuration files
CONFIG_DIR = os.path.expanduser("~/.config/devtun")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
SERVICES_FILE = os.path.join(CONFIG_DIR, "services.json")

# SSH Configuration
ssh_config = {
    "host": "",
    "port": 22,
    "user": "",
    "key_path": ""
}

def ensure_config_dir():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

def load_ssh_config():
    global ssh_config
    try:
        with open(CONFIG_FILE, "r") as file:
            ssh_config = json.load(file)
    except FileNotFoundError:
        console.print("[yellow]SSH configuration not found. Please configure it.[/yellow]")
        configure_ssh()

def save_ssh_config():
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as file:
        json.dump(ssh_config, file, indent=4)

def configure_ssh():
    ssh_config["host"] = input("Enter SSH host: ").strip()
    ssh_config["port"] = int(input("Enter SSH port (default 22): ").strip() or 22)
    ssh_config["user"] = input("Enter SSH username: ").strip()
    ssh_config["key_path"] = input("Enter SSH private key path: ").strip()

    if validate_ssh():
        save_ssh_config()
        console.print("[green]SSH configuration saved successfully.[/green]")
    else:
        console.print("[red]Failed to connect with the provided SSH configuration. Please try again.[/red]")
        configure_ssh()

def validate_ssh():
    try:
        subprocess.run([
            "ssh",
            "-i", ssh_config["key_path"],
            "-o", "BatchMode=yes",
            "-o", "ConnectTimeout=5",
            "-p", str(ssh_config["port"]),
            f"{ssh_config['user']}@{ssh_config['host']}", "exit"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def monitor_ssh_connection():
    global ssh_connected
    while True:
        ssh_connected = validate_ssh()
        time.sleep(5)

def load_services_from_file():
    global services
    try:
        with open(SERVICES_FILE, "r") as file:
            services = json.load(file)
    except FileNotFoundError:
        services = []

def save_services_to_file():
    ensure_config_dir()
    with open(SERVICES_FILE, "w") as file:
        json.dump(services, file, indent=4)

def list_services():
    if not services:
        console.print("[yellow]No services configured.[/yellow]")
        return
    table = Table(title="🚀 Configured Services")
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", style="blue")
    table.add_column("Inbound", style="green")
    table.add_column("Outbound", style="magenta")
    for idx, service in enumerate(services):
        table.add_row(
            str(idx + 1),
            service.get('service_name', 'N/A'),
            f"localhost:{service.get('local_port', 'N/A')}",
            f"{service.get('remote_host', 'N/A')}:{service.get('remote_port', 'N/A')}"
        )
    console.print(table)

def add_service():
    service_name = input("Enter service name: ").strip()
    local_port = int(input("Enter local port: ").strip())
    remote_host = input("Enter remote host: ").strip()
    remote_port = int(input("Enter remote port: ").strip())

    services.append({
        "service_name": service_name,
        "local_port": local_port,
        "remote_host": remote_host,
        "remote_port": remote_port
    })
    save_services_to_file()
    console.print("[green]Service added.[/green]")

def edit_service():
    list_services()
    idx = int(input("Enter the number of the service to edit: ").strip()) - 1
    if 0 <= idx < len(services):
        service = services[idx]
        service['service_name'] = input(f"Enter service name ({service['service_name']}): ").strip() or service['service_name']
        service['local_port'] = int(input(f"Enter local port ({service['local_port']}): ").strip() or service['local_port'])
        service['remote_host'] = input(f"Enter remote host ({service['remote_host']}): ").strip() or service['remote_host']
        service['remote_port'] = int(input(f"Enter remote port ({service['remote_port']}): ").strip() or service['remote_port'])
        save_services_to_file()
        console.print("[green]Service updated.[/green]")
    else:
        console.print("[red]Invalid selection.[/red]")

def delete_service():
    list_services()
    idx = int(input("Enter the number of the service to delete: ").strip()) - 1
    if 0 <= idx < len(services):
        confirm = input(f"Are you sure you want to delete service {services[idx]['service_name']}? (yes/no): ").strip()
        if confirm.lower() == "yes":
            services.pop(idx)
            save_services_to_file()
            console.print("[green]Service deleted.[/green]")
        else:
            console.print("[yellow]Deletion cancelled.[/yellow]")
    else:
        console.print("[red]Invalid selection.[/red]")

def update_ssh_config():
    console.print("[bold blue]Update SSH Configuration[/bold blue]")
    configure_ssh()

# --- Class quản lý Tunnel cho mỗi dịch vụ ---
class ServiceTunnel:
    def __init__(self, service_config):
        self.service_config = service_config
        self.process = None
        self.running = False

    def start(self):
        service_name = self.service_config.get("service_name", "Unknown")
        while True:
            # Nếu SSH không kết nối được, chờ và thử lại
            if not ssh_connected:
                self.running = False
                time.sleep(5)
                continue

            ssh_command = [
                "ssh",
                "-i", ssh_config["key_path"],
                "-N",
                "-L", f"{self.service_config['local_port']}:{self.service_config['remote_host']}:{self.service_config['remote_port']}",
                "-p", str(ssh_config["port"]),
                f"{ssh_config['user']}@{ssh_config['host']}"
            ]
            try:
                self.process = subprocess.Popen(ssh_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.running = True
                console.print(f"[green]Tunnel started for {service_name}[/green]")
                # Chờ tiến trình SSH kết thúc (khi tunnel bị ngắt)
                self.process.wait()
                self.running = False
                console.print(f"[red]Tunnel stopped for {service_name}. Retrying...[/red]")
            except Exception as e:
                console.print(f"[red]Error starting tunnel for {service_name}: {e}. Retrying...[/red]")
            time.sleep(5)

def show_dashboard():
    try:
        prev_stats = get_network_info()
        total_sent = 0
        total_received = 0

        while True:
            console.clear()
            console.print(Panel("[bold cyan]DevTun - SSH Port Forwarding Tool[/bold cyan]", expand=False))

            # Hiển thị trạng thái SSH
            console.print("\n[bold green]SSH Server Status:[/bold green]")
            if ssh_connected:
                console.print(f"[green]Connected to SSH Server: {ssh_config['host']}[/green]")
            else:
                console.print(f"[red]Disconnected from SSH Server: {ssh_config['host']}[/red]")

            # Thống kê Network
            current_stats = get_network_info()
            bytes_sent = current_stats['bytes_sent'] - prev_stats['bytes_sent']
            bytes_received = current_stats['bytes_recv'] - prev_stats['bytes_recv']
            total_sent += bytes_sent
            total_received += bytes_received

            console.print("\n[bold blue]Network Statistics:[/bold blue]")
            console.print(f"Bytes Sent (current): {bytes_sent / 1024:.2f} Kb/s")
            console.print(f"Bytes Received (current): {bytes_received / 1024:.2f} Kb/s")
            console.print(f"Total Bytes Sent: {total_sent / 1024:.2f} Kb")
            console.print(f"Total Bytes Received: {total_received / 1024:.2f} Kb\n\n")
            prev_stats = current_stats

            # Hiển thị trạng thái của các dịch vụ/tunnel
            table = Table(title="Running Services Dashboard")
            table.add_column("Name", style="blue")
            table.add_column("Inbound", style="green")
            table.add_column("Outbound", style="magenta")
            table.add_column("Status", style="cyan")
            for idx, tunnel in tunnels.items():
                service = tunnel.service_config
                # Kiểm tra trạng thái tunnel: nếu tiến trình tồn tại và chưa kết thúc
                if tunnel.process is not None and tunnel.process.poll() is None:
                    status = "Running"
                else:
                    status = "Stopped"
                table.add_row(
                    service.get('service_name', 'N/A'),
                    f"localhost:{service.get('local_port', 'N/A')}",
                    f"{service.get('remote_host', 'N/A')}:{service.get('remote_port', 'N/A')}",
                    status
                )

            console.print(table)
            console.print("\n[bold yellow]Press Ctrl + C to stop the program[/bold yellow]")
            time.sleep(2)
    except KeyboardInterrupt:
        confirm = input("\nAre you sure you want to stop DevTun? (yes/no): ").strip()
        if confirm.lower() == "yes":
            console.print("[green]Stopping DevTun. Goodbye![/green]")
            sys.exit(0)
        else:
            console.print("[yellow]Resuming DevTun...[/yellow]")
            show_dashboard()

def get_network_info():
    network_stats = psutil.net_io_counters()
    return {
        "bytes_sent": network_stats.bytes_sent,
        "bytes_recv": network_stats.bytes_recv,
        "packets_sent": network_stats.packets_sent,
        "packets_recv": network_stats.packets_recv
    }

def main():
    console.print("[bold green]Welcome to DevTun - Your SSH Port Forwarding Tool 🌐[/bold green]")
    ensure_config_dir()
    load_ssh_config()
    load_services_from_file()

    # Khởi chạy thread giám sát kết nối SSH liên tục
    threading.Thread(target=monitor_ssh_connection, daemon=True).start()

    global tunnels
    tunnels = {}  # reset tunnels

    while True:
        console.print("\n[bold blue]DevTun Management Menu[/bold blue]")
        console.print("1. Start All Services 🚀")
        console.print("2. List Services 📝")
        console.print("3. Add Service ➕")
        console.print("4. Edit Service ✏️")
        console.print("5. Delete Service 🗑️")
        console.print("6. Update SSH Configuration 🔧")
        console.print("0. Exit ❌")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            if not services:
                console.print("[yellow]No services configured to start.[/yellow]")
            else:
                console.print("[green]Starting services...[/green]")
                for idx, service in enumerate(services):
                    # Nếu tunnel cho dịch vụ chưa được tạo, tạo mới và chạy thread của nó
                    if idx not in tunnels:
                        tunnel = ServiceTunnel(service)
                        tunnels[idx] = tunnel
                        threading.Thread(target=tunnel.start, daemon=True).start()
                console.print("[green]All services started.[/green]")
                show_dashboard()
        elif choice == "2":
            list_services()
        elif choice == "3":
            add_service()
        elif choice == "4":
            edit_service()
        elif choice == "5":
            delete_service()
        elif choice == "6":
            update_ssh_config()
        elif choice == "0":
            confirm = input("Are you sure you want to exit DevTun? (yes/no): ").strip()
            if confirm.lower() == "yes":
                console.print("[green]Goodbye! 👋[/green]")
                break
            else:
                console.print("[yellow]Exit cancelled.[/yellow]")
        else:
            console.print("[red]Invalid choice. Please try again.[/red]")

if __name__ == "__main__":
    main()
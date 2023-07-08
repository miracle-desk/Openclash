import requests
import yaml
import subprocess
import os

def get_ping(account):
    server = account.get("server")
    ping_result = subprocess.run(["ping", "-c", "4", server], capture_output=True, text=True)
    lines = ping_result.stdout.strip().split("\n")
    last_line = lines[-1]
    if "time=" in last_line:
        ping_time = float(last_line.split("time=")[1].split(" ")[0])
        return ping_time
    else:
        return float("inf")

def get_proxies_with_lowest_ping(url, num_proxies):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text

        accounts = yaml.safe_load(data)
        filtered_accounts = [account for account in accounts.get("proxies", []) if account.get("server") and account.get("ws-opts") and account["ws-opts"].get("headers") and "Host" in account["ws-opts"]["headers"]]
        sorted_accounts = sorted(filtered_accounts, key=lambda x: get_ping(x))
        selected_accounts = sorted_accounts[:num_proxies]

        return selected_accounts
    except (requests.RequestException, yaml.YAMLError) as e:
        print(f"Error occurred while retrieving proxies: {str(e)}")
        return []

def main():
    url = "https://raw.githubusercontent.com/miracle-desk/Openclash/main/Backup/proxy_provider/filter-proxies.yaml"
    num_proxies = 40

    # Get the proxies with the lowest ping
    selected_accounts = get_proxies_with_lowest_ping(url, num_proxies)

    output_dir = "Backup/proxy_provider"
    output_path = os.path.join(output_dir, "filter-lowestPing.yaml")

    # Create the folder if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Write the selected accounts to the YAML file
    try:
        with open(output_path, "w", encoding="utf-8") as file:
            yaml.dump({"proxies": selected_accounts}, file, sort_keys=False)
        print("Akun berhasil ditulis ke file filter-lowestPing.yaml")
        print(f"Total akun yang terbaca: {len(selected_accounts)}")
    except IOError as e:
        print(f"Error occurred while writing to file: {str(e)}")

if __name__ == "__main__":
    main()

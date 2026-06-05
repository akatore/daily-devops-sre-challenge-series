#!/usr/bin/env bash
set -euo pipefail

# Menu-driven system health check script

disk_usage() {
  echo "Checking disk usage..."
  df -h
}
running_services() {
  echo "Monitoring running services..."
  ps aux
}
memory_usage() {
  echo "Assessing memory usage..."
  free -h
}
cpu_usage() {
  echo "Evaluating CPU usage..."
  top -b -n1 | head -n 10
}
send_report() {
  if ! command -v mail >/dev/null 2>&1; then
    echo "Error: mail command not found. Install mailutils or bsd-mailx and retry."
    return 1
  fi

  echo "Sending comprehensive report via email..."
  {
    echo "System Health Report"
    echo
    echo "Disk Usage:"
    df -h
    echo
    echo "Memory Usage:"
    free -h
    echo
    echo "CPU Usage:"
    top -b -n1 | head -n 10
    echo
    echo "Running Processes:"
    ps aux | head -n 20
  } > report.txt

  mail -s "System Health Report" abhijeetkatore007@gmail.com < report.txt
#   rm -f report.txt
}

while true; do
    echo "System Health Check Menu:"
    echo "1. Check Disk Usage"
    echo "2. Monitor Running Services"
    echo "3. Assess Memory Usage"
    echo "4. Evaluate CPU Usage"
    echo "5. Send Comprehensive Report via Email"
    echo "6. Exit"
    read -rp "Please select an option (1-6): " choice

    case "$choice" in
        1) disk_usage ;;
        2) running_services ;;
        3) memory_usage ;;
        4) cpu_usage ;;
        5) send_report ;;
        6) echo "Exiting..."; break ;;
        *) echo "Invalid option, please try again." ;;
    esac
    done
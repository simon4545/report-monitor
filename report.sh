#!/bin/bash

cat << 'EOF' > /root/report.sh
#!/bin/bash
get_local_ip() {
    ip=$(ip -4 addr show scope global | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep '192.168' | paste -sd, -)
    echo "Local IP: $ip"
}

get_nvidia_smi_info() {
    if command -v nvidia-smi >/dev/null 2>&1; then
        nvidia_smi_output=$(nvidia-smi --query-gpu=index,name,utilization.gpu,temperature.gpu --format=csv,noheader,nounits | paste -sd, -)
    else
        nvidia_smi_output="None"
    fi
    echo "NVIDIA SMI Info: $nvidia_smi_output"
}

get_cpu_temp() {
    cpu_temp=$(uptime | awk -F'load average: ' '{ print $2 }' | awk -F', ' '{ print $2 }')
}

report_to_server() {
    local ip=$1
    local nvidia_info=$2
    local cpu_temp=$3
    curl -X POST "http://yecao.1pan.me:5000/report" \
         -H "Content-Type: application/json" \
         -d "{\"ip\":\"$ip\",\"cpu_temp\":\"$cpu_temp\", \"nvidia_info\":\"$nvidia_info\"}"
}

while true; do
    get_local_ip
    get_nvidia_smi_info
    get_cpu_temp
    report_to_server "$ip" "$nvidia_smi_output" "$cpu_temp"
    sleep 60
done
EOF

chmod +x /root/report.sh

cat << 'EOF' > /etc/systemd/system/report.service
[Unit]
Description=Report System Information Service
After=network.target

[Service]
Type=simple
ExecStart=/root/report.sh
User=root
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable report.service
systemctl start report.service
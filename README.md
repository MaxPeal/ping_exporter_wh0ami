# Ping Exporter for Prometheus

This is a Exporter for monitoring pings to your systems with prometheus.

### Setup
```shell
root@testpi:/# cd <your app directory>
root@testpi:/opt# git clone https://git.purelinux.de/Karl/ping_exporter.git
root@testpi:/opt# cd ping_exporter
root@testpi:/opt/ping_exporter# useradd -d $(pwd) --shell /bin/false ping_exporter
root@testpi:/opt/ping_exporter# usermod -L ping_exporter
root@testpi:/opt/ping_exporter# chown -R ping_exporter:ping_exporter .
root@testpi:/opt/ping_exporter# cp config.sample.json config.json
root@testpi:/opt/ping_exporter# chmod +x exporter.py
root@testpi:/opt/ping_exporter# cp ping_exporter.service.sample /etc/systemd/system/ping_exporter.service
root@testpi:/opt/ping_exporter# vi /etc/systemd/system/ping_exporter.service # fit this file to your setup
root@testpi:/opt/ping_exporter# systemctl daemon-reload
root@testpi:/opt/ping_exporter# systemctl enable --now ping_exporter
```

The service should now run on `0.0.0.0:9102`. You can customize the listen ip and the used port in the `config.json` file.
You can call the exporter now via a GET request, e.g. `curl http://localhost:9102/?target=db.de`.

**Warning:** You will run this program with a non-root user, so your interval in the `config.json` must be at least 200ms! Otherwise the program will not work!

### Prometheus example configuration
```yaml
  - job_name: 'ping_exporter'
    metrics_path: /
    file_sd_configs:
    - files:
      - '/etc/prometheus/targets.json'
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
        replacement: ${1}
      - source_labels: [__param_target]
        regex: (.*)
        target_label: instance
        replacement: ${1}
      - source_labels: []
        regex: .*
        target_label: __address__
        replacement: 127.0.0.1:9102
```

### Example output
```
ping_packets{type="transmitted"} 5
ping_packets{type="received"} 5
ping_packets{type="lost"} 0
ping_packet_loss_percent{} 0
ping_rtt_ms{type="min"} 29.443
ping_rtt_ms{type="avg"} 30.420
ping_rtt_ms{type="max"} 30.722
ping_rtt_ms{type="mdev"} 0.515
ping_config{option="interval_ms"} 300
ping_config{option="timeout_ms"} 1000
ping_config{option="packet_bytes"} 32
ping_config{option="packet_count"} 5
ping_config{target="db.de"} 0
```

### FAQ
Q: Which types of target can I send to the exporter?  
A: The exporter can handle IPv4 addresses, IPv6 addresses and domains

Q: Can I also send a target with a port (e.g. db.de:9100) to the exporter?  
A: Yes. The exporter will detect the port and remove it autonomously.

Q: What if a host is unreachable?  
A: You will get no rtt values, the rest of the output will be shown normally in this situation.

Q: How can I control whether the config and the target will be shown in the output?  
A: Just set the `show_config` value in `config.json` to *true* or *false*.

Q: How to update the exporter?  
A: Go to the directory of the exporter and run `git pull` and `systemctl restart ping_exporter.service`.

Q: Does this exporter also run on windows?  
A: No.

Q: Is the exporter able to execute multiple requests at the same time?  
A: Yes, without any problems.

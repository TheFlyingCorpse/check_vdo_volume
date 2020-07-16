# check_vdo_volume
Checks the health of the specified VDO volume.
Returns useful metrics to be graphed if need be.

Tested on RedHat 8

# Requirements
- Assumes running with sudo privileges
- Assumes some knowledge on SElinux if SELinux is enabled
-- Hint: audit2why / audit2allow

## File /etc/sudoers.d/icinga
```
Defaults:icinga !requiretty
icinga ALL=(ALL) NOPASSWD: /usr/lib64/nagios/plugins/check_vdo_volume.py
```

## SELinux hints
```
grep icinga2_t /var/log/audit/audit.log | grep fixed_disk_device_t | audit2allow -M icinga2_vdostats
selinux -i icinga2_vdostats.pp
grep icinga2_t /var/log/audit/audit.log | grep lnk_file | audit2allow -M icinga2_vdostats2
selinux -i icinga2_vdostats2.pp
```
If that is not enough
```
tail /var/log/audit/audit.log | audit2why
```
See if anything more needs to be added

# Icinga2 CheckCommand definition
```
object CheckCommand "disk-vdo" {
    import "plugin-check-command"
    command = [
        "/usr/bin/sudo",
        "/usr/lib64/nagios/plugins/check_vdo_volume.py"
    ]
    timeout = 10s
    arguments += {
        "--critical" = {
            description = "Percent used critical"
            value = "$vdo_critical$"
        }
        "--volume" = {
            description = "Full path of vdo volume"
            value = "$vdo_volume$"
        }
        "--warning" = {
            description = "Percent used warning"
            value = "$vdo_warning$"
        }
    }
}
```

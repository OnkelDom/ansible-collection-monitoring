## Linux-Beispiel

```yaml
- name: Apply alloy
  hosts: all
  become: true
  roles:
    - role: lenmail.monitoring.alloy
```

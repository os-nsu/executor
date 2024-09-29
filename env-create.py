import argparse
from cgroup import CGroup

parser = argparse.ArgumentParser()

parser.add_argument('--env_name', type = str, required = True, help = 'environment name')
parser.add_argument('--cpu', type = int, required = True, help = 'CPU core number')
parser.add_argument('--memory', type = int, required = True, help = 'RAM size (MB)')
parser.add_argument('--disk_name', type = str, required = True, help = 'Disk name (example, nvme0n1)')
parser.add_argument('--disk_speed', type = str, required = True, help = 'Disk speed (MB/sec)')

args = parser.parse_args()
env_name = args.env_name
cpu_cores = args.cpu
memory = args.memory
disk_name = args.disk_name
disk_rw_speed = args.disk_speed

print('environment creator start...')

if not CGroup.check_controllers():
    print('cgroup controllers check failed')
    exit(-1)

cgroup = CGroup(env_name)

print(f'creating cgroup {env_name}... ')

if not cgroup.create():
    print(f'failed to create group, {env_name} already exists')
    exit(-1)

print('done')

print('Required:')
print(f'CPU: {cpu_cores} cores')
print(f'RAM: {memory} MB')
print(f'Disk name: {disk_name}')
print(f'Disk R/W speed: {disk_rw_speed} MB/sec')

print(f'adding RAM limit... ')
cgroup.set_memory_usage_limit(memory)
print(f'done')

print(f'adding CPU max cores count... ')
cgroup.set_cpu_core_count_limit(cpu_cores)
print(f'done')

print(f'adding disk RW speed limit... ')
cgroup.set_disk_rw_speed_limit(disk_name, disk_rw_speed)
print(f'done')

print(f'environment {env_name} created')
print('Use env-process-attach.py for attach process to cgroup')

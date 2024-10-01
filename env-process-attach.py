import argparse
from cgroup import CGroup

parser = argparse.ArgumentParser()
parser.add_argument('--env_name', type = str, required = True, help = 'environment name')
parser.add_argument('--pid', type = int, required = True, help = 'process id')

args = parser.parse_args()
env_name = args.env_name
pid = args.pid

cgroup = CGroup(env_name)

if not cgroup.created():
    print(f'environment {env_name} was not exist')
    exit(-1)

print(f'Adding process {pid} to environment {env_name}')
cgroup.attach_process(pid)
print('done')

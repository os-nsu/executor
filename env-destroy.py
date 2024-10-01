import argparse
from cgroup import CGroup

parser = argparse.ArgumentParser()
parser.add_argument('--env_name', type = str, required = True, help = 'environment name')

args = parser.parse_args()
env_name = args.env_name

cgroup = CGroup(env_name)

print(f'Removing {env_name} cgroup... ')

if not cgroup.created():
    print(f'cgroup {env_name} was not created')
    exit(-1)

cgroup.remove()
print('done')

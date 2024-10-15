import argparse
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # буэээ
from env_stat_utility.cgroup_stats import CgroupStats

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--env_name', type=str, required=True, help='environment name')
    args = parser.parse_args()

    cgroup_stats = CgroupStats(args.env_name)

    cgroup_stats.get_syscall_stats()


if __name__ == "__main__":
    main()

import argparse
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from syscall_stats import SyscallStats

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--env_name', type=str, required=True, help='environment name')
    parser.add_argument('--pid', '-p', type=int, help='process id')
    args = parser.parse_args()

    syscall_stats = SyscallStats(args.env_name)

    syscall_stats.get_syscall_stats(args.pid)


if __name__ == "__main__":
    main()

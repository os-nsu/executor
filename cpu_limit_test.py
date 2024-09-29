from cgroup import CGroup
import os
import unittest

cgroup = CGroup('my_env')

def get_cpu_affinity() -> int:
    with open(f"/proc/{os.getpid()}/status", "r") as f:
        for line in f.read().splitlines():
            if line.split()[0] == "Cpus_allowed_list:":
                return int(line.split()[1])
        
    return -1

class TestCPULimit(unittest.TestCase):
    def test_cpu_limit(self):
        print(f'attaching to env: my_env')
        cgroup.attach_process(os.getpid())
        self.assertEqual(get_cpu_affinity(), 2)

if __name__ == '__main__':
    unittest.main()

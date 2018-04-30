#!/bin/bash

sudo cgcreate -a ansible:ansible -t ansible:ansible -g memory:ansible_profile
if [ "$?" != "0" ]; then
    echo "ERROR: Could not create cgroup, you may need to run docker with --privileged"
    exit 1
fi

if [ -e /ansible/hacking/env-setup ]; then
    source /ansible/hacking/env-setup -q
else
    echo "WARNING: /ansible missing, did you forget to mount it?"
fi

export CGROUP_MAX_MEM_FILE=/sys/fs/cgroup/memory/ansible_profile/memory.max_usage_in_bytes
export CGROUP_CUR_MEM_FILE=/sys/fs/cgroup/memory/ansible_profile/memory.usage_in_bytes
export ANSIBLE_CALLBACK_WHITELIST=cgroup_memory_recap

cgexec -g memory:ansible_profile "$@"

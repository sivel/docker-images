# ansible_cgroup

## Building

```
docker build --no-cache -t ansible_cgroup .
```

## Using

```
docker run --rm -ti --privileged -v /path/to/playbook_dir:/playbook \
    -v /path/to/ansible/source:/ansible ansible_cgroup \
    ansible-playbook -v -i /playbook/hosts /playbook/playbook.yml
```

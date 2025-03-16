1. request timeout not handeled and can cause infinite waits !!!!! needs actual fix even if this is just example code
2. fuzzer + receive monitor before 7 hex cutoff to monirot if we are sending more then 7 hex
3. how to even detect partial loss I assume it will be registered either 0 or undefined garbage
4. fuzzer would need a map of all valid responses and requests that way we could really test robustness
5. we do not monitor or test performance in any way
6. we could validate write operations by just comparing if the received frame is the same as the sent one


#!/usr/bin/env python3
import ctypes

# clone3 系统调用号是 435
try:
    libc = ctypes.CDLL('libc.so.6', use_errno=True)
    result = libc.syscall(435, 0, 0)
    errno = ctypes.get_errno()
    print(f'clone3 syscall returned: {result}, errno: {errno}')
    if result == -1 and errno == 38:  # ENOSYS
        print('✅ clone3 is disabled (ENOSYS)')
    else:
        print(f'❌ clone3 still works or failed with different error')
except Exception as e:
    print(f'Error: {e}')

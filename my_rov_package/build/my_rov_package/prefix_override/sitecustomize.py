import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/mnt/c/Users/garci/code/rov-depth-hold/my_rov_package/install/my_rov_package'

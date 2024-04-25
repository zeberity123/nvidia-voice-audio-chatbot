import torch

print(torch.cuda.is_available())
print(torch.cuda.get_device_name(device = 0))

from tensorflow.python.client import device_lib
device_lib.list_local_devices()
import time
from datetime import datetime

now = datetime.now()
time.sleep(0.5)
print(f"compiled on {now.day}.{now.month}.{now.year} {now.hour}:{now.minute}:{now.second}")
print("acquiring MCC204 ...")
time.sleep(0.5)
print("MCC204 found!\n")

print("-------------------- mccudp --------------------")
print("Running on any IPv6 Interface on port: 4242")
print("------------------------------------------------")

while True:
    time.sleep(1)
    print("Drilldriver is running...")
    # print("Start Measurement")



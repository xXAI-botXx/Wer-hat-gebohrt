import importlib.util
import subprocess
import sys
import traceback

# check installations
print("\n-------- Checking Installations --------\n")
modules = {'numpy':'numpy', 'pandas':'pandas', 'matplotlib':'matplotlib', 'sklearn':'sklearn', 'ttkthemes':'ttkthemes', 
           'yaml':'pyyaml', 'tsfresh':'tsfresh', 'PIL':'pillow', 'webbrowser':'webbrowser'}
for module, install_name in modules.items():
    if module in sys.modules:
        print(f"Module {module} found!")
        continue
    elif importlib.util.find_spec(module) is not None:
        print(f"Module {module} found!")
        continue
    else:
        print(f"Module {module} don't found. Now program try to install it...")
        try:
            print("To solve install", install_name)
            sys.exit()
        except Exception as error:
            if "'ttkthemes']' returned non-zero exit status 1" in str(traceback.format_exc()):
                print("Problem with Tkinter installation. To solve: sudo apt-get install python3-tk")
                sys.exit()

# import own lib
sys.path.append('./src')
#sys.path.append('./')
try:   # checking PIL Error
    import anoog
    print("Module anoog found!")
except ImportError as error:
    if "Numba needs NumPy 1.20 or less" in str(error):
        print("Problem with Numpy and Numba. To solve install: pip intsall numpy==1.20.0")
        sys.exit()
    elif "cannot import name 'ImageTk' from 'PIL'" in str(error):
        print("Problem with Imagetk. To solve install: sudo apt-get install python3-pil.imagetk")
        sys.exit()

print("\n-------- Checking Finished --------\n\nSystem Output:")

# RUN the Application

data_path = '/home/anoog/rec/thema1'
anoog.automation.run(data_path=data_path, drillcapture_path='python3.8 /home/anoog/git/anoog/framework/src/anoog/', 
                                          drilldriver_path='/home/anoog/git/anoog/framework/src/anoog/data_gathering/mcc-libusb/application/mccudp', 
                                          op=anoog.automation.op.LINUX, path_to_project="/home/git/wer")

# Laptop integration
#anoog.automation.run(data_path='src/DrillDummy/testdata', drillcapture_path='src/DrillDummy/drillcapture.exe', 
#                drilldriver_path='src/DrillDummy/drilldriver.exe', 
#                op=anoog.automation.op.WINDOWS, path_to_project="./")




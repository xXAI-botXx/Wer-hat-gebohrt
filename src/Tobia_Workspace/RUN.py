import importlib.util
import subprocess
import sys
import traceback

# check installations
print("\n-------- Checking Installations --------\n")
modules = {'numpy':'numpy', 'pandas':'pandas', 'matplotlib':'matplotlib', 'sklearn':'sklearn', 'ttkthemes':'ttkthemes', 
           'yaml':'pyyaml', 'tsfresh':'tsfresh', 'PIL':'pillow'}
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
            subprocess.check_call([sys.executable, "-m", "pip", "install", install_name])
        except Exception as error:
            if "'ttkthemes']' returned non-zero exit status 1" in str(traceback.format_exc()):
                subprocess.check_call(["sudo", "apt-get", "install", "python3-tk"])
                # try again
                subprocess.check_call([sys.executable, "-m", "pip", "install", install_name])

print("\n-------- Checking Finished --------\n\nSystem Output:")


# import own lib
sys.path.append('src')
#sys.path.append('../../src')
try:   # checking PIL Error
    import anoog
except ImportError as error:
    if "Numba needs NumPy 1.20 or less" in str(error):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.20.0"])
        # try again
        import anoog
    elif "cannot import name 'ImageTk' from 'PIL'" in str(error):
        subprocess.check_call(["sudo", "apt-get", "install", "python3-pil.imagetk"])
        # try again
        import anoog


# RUN the Application
anoog.automation.run()

data_path = '/home/mustermann/rec/thema1'
#data_path = '~/rec/thema1'
#anoog.automation.run(data_path=data_path, drillcapture_path='drillcapture', drilldriver_path='drilldriver', op=anoog.automation.op.LINUX)





import os
import subprocess
import sys

def setup():
    setup_dir()
    setup_package()

def setup_dir():
    os.makedirs('mov',exist_ok=True)
    os.makedirs('img',exist_ok=True)
    os.makedirs('test_folder',exist_ok=True)
    os.makedirs('data',exist_ok=True)

def setup_package():
    reqire_path = 'requirements.txt'
    subprocess.check_call([sys.executable,"-m","pip","install","-r",reqire_path])

if __name__ == "__main__":
    setup()
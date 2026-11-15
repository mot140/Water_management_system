from src.camera_setting import camera_starting
import glob

def main():
    files = read_video_path_list()
    print("Files to process:", files)
    for file in files:
        camera_starting(file)

def read_video_path_list():
    files = glob.glob("mov/*.MOV")
    return files

if __name__ == "__main__":
    main()
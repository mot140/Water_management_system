import os
import cv2

#画像の表示
def save_frame(frame, dir_path:str, frame_number:str, ext="png"):
    target_dir = os.path.join("img", dir_path)
    os.makedirs(target_dir, exist_ok=True)
    result_path = os.path.join(target_dir, f"{frame_number}.{ext}")
    cv2.imwrite(result_path, frame)
    return result_path


def get_next_dir_number(video_path,base_path="img"):
    video_stem = os.path.splitext(os.path.basename(video_path))[0]
    output_dir = os.path.join(base_path, video_stem)
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n--- [get_output_dir_by_filename] 実行結果 ---")
    print(f"  保存先フォルダ: '{output_dir}/'")
    return output_dir


if __name__ == "__main__":
    # 次のフォルダ番号を取得
    next_folder_num = get_next_dir_number("img")
    print(next_folder_num)


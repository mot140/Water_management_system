import os
import cv2
import csv

#画像の表示
def save_frame(frame, dir_path:str, frame_number:str, ext="png"):
    target_dir = os.path.join("img", dir_path)
    os.makedirs(target_dir, exist_ok=True)
    result_path = os.path.join(target_dir, f"{frame_number}.{ext}")
    cv2.imwrite(result_path, frame)
    return result_path


def get_next_dir_number(base_path="img"):
    """指定したフォルダ（例: img/）内にある数値フォルダの最大値を取得し、次の番号（最大値 + 1）を返す"""
    print(f"\n--- [get_next_dir_number] 実行結果 ---")
    print(f"  検索対象: '{base_path}/'")

    # ベースフォルダが存在しない場合は作成して 1 を返す
    if not os.path.exists(base_path):
        print(
            f"  └ '{base_path}' フォルダが存在しないため、初回番号 『1』 を返します。"
        )
        return 1
    dir_numbers = []
    # フォルダ内の全要素を取得
    for entry in os.listdir(base_path):
        full_path = os.path.join(base_path, entry)
        # 「フォルダである」かつ「名前が数値である」ものを抽出 (例: "1", "2")
        if os.path.isdir(full_path) and entry.isdigit():
            dir_numbers.append(int(entry))
    if dir_numbers:
        max_num = max(dir_numbers)
        next_num = max_num + 1
        return next_num
    else:
        return 1


if __name__ == "__main__":
    # 次のフォルダ番号を取得
    next_folder_num = get_next_dir_number("img")
    print(next_folder_num)


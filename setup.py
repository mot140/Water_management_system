import os
import subprocess
import sys
import re
from importlib import metadata

def setup():
    setup_dir()
    setup_package()

def setup_dir():
    os.makedirs('mov',exist_ok=True)
    os.makedirs('img',exist_ok=True)
    os.makedirs('test_folder',exist_ok=True)
    os.makedirs('data',exist_ok=True)

def setup_package(req_path="requirements.txt"):
    if not os.path.exists(req_path):
        print(f"[警告] '{req_path}' が見つかりません。")
        return

    # 1. 現在インストール済みのパッケージ名をすべて小文字で取得（ハイフン・アンダースコアを統一）
    installed_packages = {
        dist.metadata["Name"].lower().replace("_", "-")
        for dist in metadata.distributions()
        if dist.metadata.get("Name")
    }

    # 2. requirements.txt から未インストールのものだけを抽出
    missing_packages = []
    with open(req_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # 空行やコメント行(#)はスキップ
            if not line or line.startswith("#"):
                continue

            # "lightgbm>=4.0.0" や "opencv-python==4.9.0.80" からパッケージ名だけを抽出
            pkg_name = re.split(r"[=<>!~;\[]", line)[0].strip().lower().replace("_", "-")
            if pkg_name not in installed_packages:
                missing_packages.append(line)

    # 3. すべてインストール済みなら pip を実行せずにパスする
    if not missing_packages:
        print("[スキップ] 必要なパッケージはすべてインストール済みです。")
        return
    print(f"[インストール実行] 未導入パッケージを導入します: {missing_packages}")
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])
if __name__ == "__main__":
    setup()
import cv2
import numpy as np
import matplotlib.pyplot as plt

def blue_detect(img):
    """HSVでの青色抽出"""
    Blue_MIN = np.array([85, 50, 50])
    Blue_Max = np.array([135, 255, 255])
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_img, Blue_MIN, Blue_Max)

    # ★ノイズ除去（オープニング処理）をここで実行
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask


def get_centers(binary_img, min_area=15):
    """ラベリング処理により指定面積以上の全ビーズの重心座標(x, y)リストを取得"""
    nlabels, labels, stats, centers = cv2.connectedComponentsWithStats(
        binary_img
    )

    # 背景（ラベル0）を除外
    if nlabels <= 1:
        return []

    detected_centers = []
    # ラベル1以降（各オブジェクト）を処理
    for i in range(1, nlabels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= min_area:  # ノイズでない一定サイズ以上のビーズのみ抽出
            cx = int(centers[i][0])
            cy = int(centers[i][1])
            detected_centers.append((cx, cy))

    return detected_centers


def drawOrbit(tracks, frame):
    """保存されているすべてのビーズ軌跡を画面に描画"""
    for bead_id, history in tracks.items():
        # 過去の軌跡を線で描画
        if len(history) > 1:
            pts = np.array(history, np.int32).reshape((-1, 1, 2))
            cv2.polylines(
                frame, [pts], isClosed=False, color=(0, 255, 255), thickness=2
            )

        # 現在位置（最新の点）に緑丸を描画
        current_pt = history[-1]
        cv2.circle(frame, current_pt, 5, (0, 255, 0), thickness=-1)

def plot_trajectories(
    tracks, width=400, height=800, save_path="bead_trajectories.png"
):
    """ビーズの全軌跡を Matplotlib の 2D 散布図/折れ線グラフで描画・保存する"""

    if not tracks:
        print("【警告】軌跡データ (tracks) が空のため、グラフを描画できません。")
        return

    plt.figure(figsize=(6, 10))

    # 画像の座標系に合わせて Y 軸を反転（上が 0、下が height）
    plt.xlim(0, width)
    plt.ylim(height, 0)

    valid_beads = 0
    for bead_id, history in tracks.items():
        if len(history) < 3:  # ノイズ（瞬く間に消えた点）は除外
            continue

        xs = [pt[0] for pt in history]
        ys = [pt[1] for pt in history]

        # 軌跡（線）を描画
        plt.plot(xs, ys, alpha=0.7, linewidth=2, label=f"Bead #{bead_id}")

        # 開始位置（緑の丸）と 最終・滞留位置（赤の×）をプロット
        plt.scatter(xs[0], ys[0], color="green", s=30, zorder=5)
        plt.scatter(xs[-1], ys[-1], color="red", marker="x", s=50, zorder=5)

        valid_beads += 1

    plt.title(
        f"Bead Trajectories (Total: {valid_beads} beads)",
        fontsize=12,
        weight="bold",
    )
    plt.xlabel("X Position (px)")
    plt.ylabel("Y Position (px)")
    plt.grid(True, linestyle="--", alpha=0.5)

    # アスペクト比をトレイの実際の比率（1:2）に固定
    plt.gca().set_aspect("equal", adjustable="box")

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"軌跡グラフを保存しました: {save_path}")
    plt.show()

def process_frame(img, tracks, max_distance=40):
    """1フレームごとの検出とトラッキング（軌跡の更新）"""
    mask = blue_detect(img)
    centers = get_centers(mask)

    # 簡易トラッキング（前フレームの点と紐付け）
    new_tracks = {}
    used_centers = set()

    # 既存のビーズIDとの距離計算による紐付け
    for bead_id, history in tracks.items():
        last_pos = history[-1]
        best_dist = float("inf")
        best_idx = -1

        for idx, center in enumerate(centers):
            if idx in used_centers:
                continue
            dist = np.hypot(center[0] - last_pos[0], center[1] - last_pos[1])
            if dist < best_dist and dist < max_distance:
                best_dist = dist
                best_idx = idx

        if best_idx != -1:
            new_tracks[bead_id] = history + [centers[best_idx]]
            used_centers.add(best_idx)
        else:
            new_tracks[bead_id] = history  # 見失った場合も履歴保持

    # 新しく現れたビーズに新規IDを割り当て
    next_id = max(tracks.keys(), default=-1) + 1
    for idx, center in enumerate(centers):
        if idx not in used_centers:
            new_tracks[next_id] = [center]
            next_id += 1

    # 軌跡の描画
    drawOrbit(new_tracks, img)

    return img, new_tracks
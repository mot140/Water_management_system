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
    chunk = split_img(img)
    mask = blue_detect(img)
    centers = get_centers(mask)
    draw = draw_Orbit(centers,chunk,img)
    #draw_pqint = draw_Orbit(centers,chunk)
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


def split_img(frame, rows=80, cols=40, preview=True, output_grid_path="grid_result.png"):
    chunks = []
    h, w = frame.shape[:2]
    frame_copy = frame.copy()

    # 1. チャンクの分割切り出し
    for row_img in np.array_split(frame, rows, axis=0):
        for chunk in np.array_split(row_img, cols, axis=1):
            chunks.append(chunk)

    # 2. 横線（Y軸方向）の描画
    row_splits = np.array_split(np.arange(h), rows)
    for row_indices in row_splits:
        y = row_indices[0]
        cv2.line(frame_copy, (0, y), (w, y), (0, 0, 255), 1)
    cv2.line(frame_copy, (0, h - 1), (w, h - 1), (0, 0, 255), 1)

    # 3. 縦線（X軸方向）の描画
    col_splits = np.array_split(np.arange(w), cols)
    for col_indices in col_splits:
        x = col_indices[0]
        cv2.line(frame_copy, (x, 0), (x, h), (0, 0, 255), 1)
    cv2.line(frame_copy, (w - 1, 0), (w - 1, h), (0, 0, 255), 1)


    # 5. グリッド線付き全体画像の保存・表示
    cv2.imwrite(output_grid_path, frame_copy)
    print(f"グリッド付き全体系画像を保存しました: {output_grid_path}")
    
    if preview:
        cv2.imshow("Full Image with Grid", frame_copy)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return chunks

def draw_Orbit(centers, chunks, frame, rows=80, cols=40):
    """
    1フレーム内の全 center 座標と chunks を受け取り、
    青色検証・格子セルの緑色着色・中心点描画をまとめて実行する関数（追跡なし）

    :param centers: ビーズの中心座標リスト [(x1, y1), (x2, y2), ...]
    :param chunks: split_img で生成された全格子セル画像のリスト (3200個)
    :param frame: 描画対象のフレーム画像
    :param rows: 行数 (80)
    :param cols: 列数 (40)
    :return: 描画・着色後の frame, 着色された格子セル座標リスト [(r, c), ...]
    """
    h, w = frame.shape[:2]
    overlay = frame.copy()
    colored_cells = []

    row_splits = np.array_split(np.arange(h), rows)
    col_splits = np.array_split(np.arange(w), cols)

    for cx, cy in centers:
        if 0 <= cx < w and 0 <= cy < h:
            # 1. 重心座標 (cx, cy) から 80x40 の 行 (r) と 列 (c) を算出
            c = int(cx // (w / cols))
            r = int(cy // (h / rows))

            r = min(max(r, 0), rows - 1)
            c = min(max(c, 0), cols - 1)

            # 2. 該当する chunk を取得
            idx = r * cols + c
            chunk = chunks[idx]

            # 3. chunk 内の BGR 画素値を利用した青色判定
            blue_channel = chunk[:, :, 0]
            red_channel = chunk[:, :, 2]
            blue_pixels = np.count_nonzero((blue_channel > 90) & (blue_channel > red_channel + 20))

            # 4. 青色判定を満たした場合、格子セルを塗りつぶし対象に登録
            if blue_pixels >= 3:
                colored_cells.append((r, c))
                y1, y2 = row_splits[r][0], row_splits[r][-1]
                x1, x2 = col_splits[c][0], col_splits[c][-1]
                cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), -1)

            # 5. 中心位置に緑色の丸を描画
            cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

    # 緑色着色レイヤーを一括で半透明合成 (透過度 0.4)
    frame_result = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)

    return frame_result, colored_cells
    

if __name__ == "__main__":
    img = cv2.imread("last_frame.png")
    if img is not None:
        chunks = split_img(img, rows=80, cols=40)
    else:
        print("画像ファイルの読み込みに失敗しました。パスを確認してください。")

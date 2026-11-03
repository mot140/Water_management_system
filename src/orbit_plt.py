import cv2
import numpy as np
import matplotlib.pyplot as plt
import csv

ROWS, COLS = 80, 40


def blue_detect(img):
    """HSVでの青色抽出"""
    Blue_MIN = np.array([85, 50, 50])
    Blue_Max = np.array([135, 255, 255])
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_img, Blue_MIN, Blue_Max)

    # ノイズ除去（オープニング処理）
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask


def get_centers(binary_img, min_area=15):
    """ラベリング処理により指定面積以上の全ビーズの重心座標(x, y)リストを取得"""
    nlabels, labels, stats, centers = cv2.connectedComponentsWithStats(binary_img)

    if nlabels <= 1:
        return []

    detected_centers = []
    for i in range(1, nlabels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= min_area:
            cx = int(centers[i][0])
            cy = int(centers[i][1])
            detected_centers.append((cx, cy))

    return detected_centers

def cell_rect(r, c, w, h, rows=ROWS, cols=COLS):
    """セル(r, c)の画素範囲 (x1, y1, x2, y2) を返す"""
    x1, x2 = c * w // cols, (c + 1) * w // cols - 1
    y1, y2 = r * h // rows, (r + 1) * h // rows - 1
    return x1, y1, x2, y2


def save_cells_csv(records, save_path="colored_cells.csv"):
    """
    塗ったセルの座標をCSVに出力する。
    records: [{"frame": int, "row": int, "col": int, "x1": .., "y1": .., "x2": .., "y2": ..}, ...]
    """
    if not records:
        print("【警告】記録されたセルがないため、CSVを出力しません。")
        return

    fieldnames = ["frame", "row", "col", "x1", "y1", "x2", "y2"]
    # utf-8-sig: Excelで開いても文字化けしない
    with open(save_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"塗ったセルの座標をCSVに保存しました: {save_path} ({len(records)}行)")


def touched_cells(cx, cy, w, h, rows=ROWS, cols=COLS, radius=5):
    """
    center(cx, cy)を中心とする半径 radius の円に触れている格子セル (r, c) のリストを返す。
    radius=0 の場合は center を含むセル1つだけ。
    """
    cells = []

    # 候補となるセルの範囲（円の外接矩形がかかる行・列）
    c_min = max((cx - radius) * cols // w, 0)
    c_max = min((cx + radius) * cols // w, cols - 1)
    r_min = max((cy - radius) * rows // h, 0)
    r_max = min((cy + radius) * rows // h, rows - 1)

    for r in range(r_min, r_max + 1):
        y1, y2 = r * h // rows, (r + 1) * h // rows - 1
        for c in range(c_min, c_max + 1):
            x1, x2 = c * w // cols, (c + 1) * w // cols - 1

            # セル矩形上で center に最も近い点までの距離
            nx = min(max(cx, x1), x2)
            ny = min(max(cy, y1), y2)
            if np.hypot(cx - nx, cy - ny) <= radius:
                cells.append((r, c))

    return cells


def fill_cells(frame, centers, rows=ROWS, cols=COLS, color=(0, 255, 0), alpha=0.4, touch_radius=5):
    """
    center座標に触れている格子セルを塗りつぶす。
    :return: 着色後のframe, 着色されたセルの集合 {(r, c), ...}
    """
    h, w = frame.shape[:2]
    overlay = frame.copy()
    colored_cells = set()

    for cx, cy in centers:
        if not (0 <= cx < w and 0 <= cy < h):
            continue

        for r, c in touched_cells(cx, cy, w, h, rows, cols, touch_radius):
            if (r, c) in colored_cells:
                continue
            colored_cells.add((r, c))

            x1, x2 = c * w // cols, (c + 1) * w // cols - 1
            y1, y2 = r * h // rows, (r + 1) * h // rows - 1
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)

    result = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
    return result, colored_cells


def draw_grid_lines(frame, rows=ROWS, cols=COLS, color=(0, 0, 255), thickness=1):
    """格子線を frame に直接描画する"""
    h, w = frame.shape[:2]

    for r in range(rows + 1):
        y = min(r * h // rows, h - 1)
        cv2.line(frame, (0, y), (w - 1, y), color, thickness)

    for c in range(cols + 1):
        x = min(c * w // cols, w - 1)
        cv2.line(frame, (x, 0), (x, h - 1), color, thickness)

    return frame


def drawOrbit(tracks, frame):
    """保存されているすべてのビーズ軌跡を画面に描画"""
    for bead_id, history in tracks.items():
        if len(history) > 1:
            pts = np.array(history, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=False, color=(0, 255, 255), thickness=2)

        current_pt = history[-1]
        cv2.circle(frame, current_pt, 5, (0, 255, 0), thickness=-1)


def plot_trajectories(tracks, width=400, height=800, save_path="bead_trajectories.png"):
    """ビーズの全軌跡を Matplotlib で描画・保存する"""
    if not tracks:
        print("【警告】軌跡データ (tracks) が空のため、グラフを描画できません。")
        return

    plt.figure(figsize=(6, 10))
    plt.xlim(0, width)
    plt.ylim(height, 0)

    valid_beads = 0
    for bead_id, history in tracks.items():
        if len(history) < 3:
            continue

        xs = [pt[0] for pt in history]
        ys = [pt[1] for pt in history]

        plt.plot(xs, ys, alpha=0.7, linewidth=2, label=f"Bead #{bead_id}")
        plt.scatter(xs[0], ys[0], color="green", s=30, zorder=5)
        plt.scatter(xs[-1], ys[-1], color="red", marker="x", s=50, zorder=5)
        valid_beads += 1

    plt.title(f"Bead Trajectories (Total: {valid_beads} beads)", fontsize=12, weight="bold")
    plt.xlabel("X Position (px)")
    plt.ylabel("Y Position (px)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.gca().set_aspect("equal", adjustable="box")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"軌跡グラフを保存しました: {save_path}")
    plt.show()


def process_frame(img, tracks, max_distance=40, draw_orbit=False, show_grid=True, touch_radius=5,frame_no=0, records=None):
    """1フレームごとの検出・格子の塗りつぶし・格子線表示・トラッキング"""
    mask = blue_detect(img)
    centers = get_centers(mask)
    h, w = img.shape[:2] 
    # centerに触れている格子セルを塗る
    img, colored_cells = fill_cells(img, centers, touch_radius=touch_radius)
    # ↓ 追加：塗ったセルの座標を記録（行・列の順に並べる）
    if records is not None:
        for r, c in sorted(colored_cells):
            x1, y1, x2, y2 = cell_rect(r, c, w, h)
            records.append(
                {"frame": frame_no, "row": r, "col": c, "x1": x1, "y1": y1, "x2": x2, "y2": y2}
            )
    # 塗りつぶしの上に格子線を重ねる
    if show_grid:
        draw_grid_lines(img)

    # 簡易トラッキング（前フレームの点と紐付け）
    new_tracks = {}
    used_centers = set()

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
            new_tracks[bead_id] = history

    next_id = max(tracks.keys(), default=-1) + 1
    for idx, center in enumerate(centers):
        if idx not in used_centers:
            new_tracks[next_id] = [center]
            next_id += 1

    if draw_orbit:
        drawOrbit(new_tracks, img)

    return img, new_tracks


if __name__ == "__main__":
    img = cv2.imread("last_frame.png")
    if img is not None:
        out, tracks = process_frame(img, {})
        cv2.imwrite("grid_result.png", out)
        cv2.imshow("Grid + Filled Cells", out)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("画像ファイルの読み込みに失敗しました。パスを確認してください。")
import cv2
import numpy as np
from .orbit_plt import *
from .save_frame import *
import os
# ★1. pointsはグローバル領域で定義する
points = []


def mouse_callback(event, x, y, flags, params):
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append((x, y))
            print(f"点 {len(points)} を指定: ({x}, {y})")




def camera_starting(video_path):
    global points
    points = []  # 再実行用に初期化
    OUT_WIDTH = 400
    OUT_HEIGHT = 800
    folder = get_next_dir_number()
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(fps)
    cnt = 0
    tracks = {}
    records = []          # ← 追加：塗ったセルの記録用
    frame_no = 0
    if not cap.isOpened():
        print("動画を開けませんでした")
        return
    ret, frame = cap.read()
    print(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
    if not ret:
        print("フレームの読み込みに失敗しました")
        return

    WINDOW_NAME = "Select 4 Corners (TL -> TR -> BR -> BL)"
    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, mouse_callback)

    print("トレイの4角を [左上 -> 右上 -> 右下 -> 左下] の順でクリックしてください。")
    print("4点選択後、EnterまたはSpaceキーを押すと確定します。")
    cell_dict, All_cells = new_count_cells()  
    # 手動指定のループ
    while True:
        display_img = frame.copy()

        # クリックした点と番号の描画
        for idx, pt in enumerate(points):
            cv2.circle(display_img, pt, 5, (0, 0, 255), -1)
            cv2.putText(
                display_img,
                str(idx + 1),
                (pt[0] + 10, pt[1] + 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        # 4点揃ったら青い線で囲む
        if len(points) == 4:
            pts = np.array(points, np.int32).reshape((-1, 1, 2))
            cv2.polylines(display_img, [pts], True, (255, 0, 0), 2)

        # ★2. 毎フレーム描画を更新表示する
        cv2.imshow(WINDOW_NAME, display_img)

        # ★3. 4点揃った状態での確定キー（Enter: 13, Space: 32）待ち
        key = cv2.waitKey(1) & 0xFF
        if len(points) == 4 and (key == 13 or key == 32):
            break
        elif key == 27:  # ESCで中断
            cap.release()
            cv2.destroyAllWindows()
            return

    cv2.destroyAllWindows()

    # 透視変換用の変換行列 M を計算
    src_pts = np.float32(points)
    dst_pts = np.float32(
        [[0, 0], [OUT_WIDTH, 0], [OUT_WIDTH, OUT_HEIGHT], [0, OUT_HEIGHT]]
    )
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)

    # 全フレームの変換処理ループ
    # 全フレームの変換処理ループ
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    tracks = {}
    save_frame(display_img,str(folder),str(cnt))
    while cap.isOpened():
        ret, frame = cap.read()
        cnt += 1
        if not ret:
            break
        cropped_frame = cv2.warpPerspective(frame, M, (OUT_WIDTH, OUT_HEIGHT))

        # --------------------------------------------------
        # ★ ここを追加・修正します！
        # process_frame に cropped_frame と tracks を渡して検出＆描画を実行
        # --------------------------------------------------
        cropped_frame, tracks,cell_dict = process_frame(cropped_frame, tracks,cell_dic=cell_dict,frame_no=frame_no,records=records)

        cv2.imshow("Cropped & Normalized Frame", cropped_frame)
        save_frame(cropped_frame,str(folder),str(cnt))
        if cv2.waitKey(30) & 0xFF == 27:  # ESCキーで終了
            break

    cap.release()
    cv2.destroyAllWindows()
    plot_trajectories(tracks, OUT_WIDTH, OUT_HEIGHT)
    save_cells_csv(records, "colored_cells.csv")
    #sum_colored_cells(cell_dict)  # ← 追加：総塗りつぶしセル数を表示
    ave = cells_ave(cell_dict)
    print(ave)
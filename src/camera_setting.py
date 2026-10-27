import cv2
import numpy as np

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

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("動画を開けませんでした")
        return

    ret, frame = cap.read()
    if not ret:
        print("フレームの読み込みに失敗しました")
        return

    WINDOW_NAME = "Select 4 Corners (TL -> TR -> BR -> BL)"
    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, mouse_callback)

    print("トレイの4角を [左上 -> 右上 -> 右下 -> 左下] の順でクリックしてください。")
    print("4点選択後、EnterまたはSpaceキーを押すと確定します。")

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
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        cropped_frame = cv2.warpPerspective(frame, M, (OUT_WIDTH, OUT_HEIGHT))

        # --------------------------------------------------
        # ここに今後、ビーズ検出や滞留判定の処理を追加します
        # --------------------------------------------------

        cv2.imshow("Cropped & Normalized Frame", cropped_frame)
        if cv2.waitKey(30) & 0xFF == 27:  # ESCキーで終了
            break

    cap.release()
    cv2.destroyAllWindows()
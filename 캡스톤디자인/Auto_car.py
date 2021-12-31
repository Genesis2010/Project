import cv2
import numpy as np
import matplotlib.pyplot as plt
import serial
import time

# cap = cv2.VideoCapture("./video/blog_test.mp4")
cap = cv2.VideoCapture("./video/project_test/12.h264")
# cap = cv2.VideoCapture(-1)

frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

#fourcc = cv2.VideoWriter_fourcc(*'XVID')
#out1 = cv2.VideoWriter('/Users/genesis/Desktop', fourcc, 30.0, frame_size)

# Bird Eye View
def wrapping(image):

    (h, w) = (image.shape[0], image.shape[1])

    source = np.float32([[240, 434], [530, 434], [280, 350], [620, 350]])
    destination = np.float32([[120, h], [500, h], [150, 0], [610, 0]])

    transform_matrix = cv2.getPerspectiveTransform(source, destination)
    minv = cv2.getPerspectiveTransform(destination, source)
    _image = cv2.warpPerspective(image, transform_matrix, (w, h))

    return _image, minv

def roi(image):
    x = int(image.shape[1])
    y = int(image.shape[0])

    _shape = np.array([[int(0.1*x), int(y)], [int(0.1*x), int(0.1*y)], [int(0.4*x), int(0.1*y)], [int(0.4*x), int(y)], [int(0.7*x), int(y)], [int(0.7*x), int(0.1*y)], [int(0.9*x), int(0.1*y)], [int(0.9*x), int(y)], [int(0.2*x), int(y)]])

    mask = np.zeros_like(image)

    if len(image.shape) > 2:
        channel_count = image.shape[2]
        ignore_mask_color = (255,) * channel_count
    else :
        ignore_mask_color = 255

    cv2.fillPoly(mask, np.int32([_shape]), ignore_mask_color)
    masked_image = cv2.bitwise_and(image, mask)

    # ploygons = np.array([
    #     [(140, 480), (0, 350), (500, 350), (640, 480)]
    # ])
    # mask = np.zeros_like(image)  # mask는 이미지와 같고 모든 픽셀은 0으로 된다
    # cv2.fillPoly(mask, ploygons, 255)  # 관심영역을 채우기 위해 사용
    # masked_image = cv2.bitwise_and(image, mask)
    # return masked_image

    return masked_image

def region_of_interest(image):

    ploygons = np.array([
        [(140, 480), (140, 350), (500, 350), (640, 480)]
    ])
    mask = np.zeros_like(image)  # mask는 이미지와 같고 모든 픽셀은 0으로 된다
    cv2.fillPoly(mask, ploygons, 255)  # 관심영역을 채우기 위해 사용
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image

def plothistogram(image): #240
    histogram = np.sum(image[image.shape[0]//2:,:], axis=0)
    midpoint = int(histogram.shape[0]/2)
    leftbase = np.argmax(histogram[:midpoint])
    rightbase = np.argmax(histogram[midpoint:]) + midpoint

    #print(image.shape[0]//2)

    return leftbase, rightbase

def slide_window_search(binary_warped, left_current, right_current):
    out_img = np.dstack((binary_warped, binary_warped, binary_warped))

    nwindows = 5
    window_height = int(binary_warped.shape[0] / nwindows)
    nonzero = binary_warped.nonzero() # 선이 있는 부분의 인덱스나 저장
    nonzero_y = np.array(nonzero[0])
    nonzero_x = np.array(nonzero[1])
    margin = 100
    minpix = 50
    left_lane = []
    right_lane = []
    color = [0, 255, 0]
    thickness = 2


    for w in range(nwindows):
        win_y_low = binary_warped.shape[0] - (w + 1) * window_height
        win_y_high = binary_warped.shape[0] - w * window_height
        win_xleft_low = left_current - margin
        win_xleft_high = left_current + margin
        win_xright_low = right_current - margin
        win_xright_high = right_current + margin

        cv2.rectangle(out_img, (win_xleft_low, win_y_low), (win_xleft_high, win_y_high), color, thickness)
        cv2.rectangle(out_img, (win_xright_low, win_y_low), (win_xright_high, win_y_high), color, thickness)
        good_left = ((nonzero_y >= win_y_low) & (nonzero_y < win_y_high) & (nonzero_x >= win_xleft_low)& ( nonzero_x < win_xleft_high)).nonzero()[0]
        good_right = ((nonzero_y >= win_y_low) & (nonzero_y < win_y_high) & (nonzero_x >= win_xright_low)& ( nonzero_x < win_xright_high)).nonzero()[0]
        left_lane.append(good_left)
        right_lane.append(good_right)

        if len(good_left) > minpix:
            left_current = int(np.mean(nonzero_x[good_left]))
        if len(good_right) > minpix:
            right_current = int(np.mean(nonzero_x[good_right]))

    left_lane = np.concatenate(left_lane) # array를 1차원으로 합침
    right_lane = np.concatenate(right_lane)

    leftx = nonzero_x[left_lane]
    lefty = nonzero_y[left_lane]
    rightx = nonzero_x[right_lane]
    righty = nonzero_y[right_lane]



    left_fit = np.polyfit(lefty, leftx, 2)
    right_fit = np.polyfit(righty, rightx, 2)

    print("왼쪽 차선 곡률1 ", left_fit[0], "오른쪽 차선 곡률1 ", right_fit[0])

    ploty = np.linspace(0, binary_warped.shape[0] - 1, binary_warped.shape[0])
    left_fitx = left_fit[0] * ploty ** 2 + left_fit[1] * ploty + left_fit[2]
    right_fitx = right_fit[0] * ploty ** 2 + right_fit[1] * ploty + right_fit[2]




    ltx = np.trunc(left_fitx)
    rtx = np.trunc(right_fitx)

    # print("왼쪽 차선 곡률2 ", ltx)
    # print("오른쪽 차선 곡률2", rtx)



    out_img[nonzero_y[left_lane], nonzero_x[left_lane]] = [255, 0, 0]
    out_img[nonzero_y[right_lane], nonzero_x[right_lane]] = [0, 0, 255]

    # plt.imshow(out_img)
    # plt.plot(left_fitx, ploty, color = 'yellow')
    # plt.plot(right_fitx, ploty, color = 'yellow')
    # plt.show()

    # print(left_fitx, right_fitx, ploty)


    ret = {'left_fitx' : ltx, 'right_fitx' : rtx, 'ploty' : ploty}

    return ret

def draw_lane_lines(original_image, warped_image, Minv, draw_info):
    left_fitx = draw_info['left_fitx']
    right_fitx = draw_info['right_fitx']
    ploty = draw_info['ploty']

    warp_zero = np.zeros_like(warped_image).astype(np.uint8)
    color_warp = np.dstack((warp_zero, warp_zero, warp_zero))

    pts_left = np.array([np.transpose(np.vstack([left_fitx, ploty]))])
    pts_right = np.array([np.flipud(np.transpose([right_fitx, ploty]))])
    pts = np.hstack((pts_left, pts_right))

    mean_x = np.mean((left_fitx, right_fitx), axis = 0)
    pts_mean = np.array([np.flipud(np.transpose(np.vstack([mean_x, ploty])))])

    cv2.fillPoly(color_warp, np.int_([pts]), (216, 168, 74))
    # cv2.fillPoly(color_warp, np.int_([pts_mean]), (216, 168, 74))
    cv2.polylines(color_warp, np.int_([pts_mean]), False, (255, 255, 255), 3, 16)

    newwarp = cv2.warpPerspective(color_warp, Minv, (original_image.shape[1], original_image.shape[0]))
    result = cv2.addWeighted(original_image, 1, newwarp, 0.4, 0)

    return pts_mean, result

# port = "/dev/ttyUSB0"
# serialToArduino = serial.Serial(port, 9600)

# while True:
#     c = input()
#     if c == 'q':
#         break;
#     else:
#         C = c.encode('utf-8')
#         serialToArduino.write(C)

cap.set(3,640)
cap.set(4,480)

while True :
    retval, img = cap.read()
    if not retval:
        break

    ## 조감도, wrapped img
    wrapped_img, minverse = wrapping(img)

    ## 조감도 필터링
    w_f_r_img = roi(wrapped_img)

    ## 조감도 필터링 자르기
    w_f_r_img = region_of_interest(wrapped_img)

    ## 조감도 선 따기 wrapped img threshold
    _gray = cv2.cvtColor(wrapped_img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(_gray, 160, 255, cv2.THRESH_BINARY)

    ## 선 분포도 조사 histogram
    leftbase, rightbase = plothistogram(thresh)

    ## histogram 기반 window roi 영역
    draw_info = slide_window_search(thresh, leftbase, rightbase)

    ## 원본 이미지에 라인 넣기
    meanPts, result = draw_lane_lines(img, thresh, minverse, draw_info)

    #out1.write(result)
    cv2.imshow('result', result)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
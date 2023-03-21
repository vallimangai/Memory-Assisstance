from tensorflow import keras

import cv2

face_cascade = cv2.CascadeClassifier('faces.xml')
def detect_face(img):
    img = cv2.imread(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    # Draw rectangle around the faces
    for (x, y, w, h) in faces:
        img = img[x:x + w, y:y + h]
    return img
def get_arr_img(img):
  # img_array = cv2.imread(img,cv2.IMREAD_GRAYSCALE)
  print("shape: ",img.shape)
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  return cv2.resize(gray, (100, 100))
def check_sim(img1,img2):
    reconstructed_model = keras.models.load_model("my_model.h5")
    # print(reconstructed_model.summary())

    img1=get_arr_img(detect_face(img1))
    img2=get_arr_img(detect_face(img2))
    print(img1.shape)
    return(reconstructed_model.predict([img1.reshape((1, 100, 100)),
                   img2.reshape((1, 100, 100))]).flatten()[0])
# check_sim("img1.png","img2.png")
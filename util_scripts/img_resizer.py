import os 
import cv2 as cv

def resize_channels(img,new_h,new_b):
    B,G,R = cv.split(img)
    B = cv.resize(B,(new_h,new_b))
    G = cv.resize(G,(new_h,new_b))
    R = cv.resize(R,(new_h,new_b))
    img = cv.merge([B,G,R])
    return img

input_dir = "/home/satarw/webapp_image_aesthetics/Images/Orginal_temple_images"
output_dir = "/home/satarw/webapp_image_aesthetics/Images/resized_images"

for filename in os.listdir(input_dir):
    img = cv.imread(os.path.join(input_dir,filename))
    img = resize_channels(img,256,256)
    cv.imwrite(os.path.join(input_dir, f"{filename}_final"),img)
    h0 = img.shape[0]
    b0 = img.shape[1]
    for i in range(4,19):
        r = i/10
        nh = int(b0*r)
        nb = int(h0*r)
        B,G,R = cv.split(img)
        new_img_b_const = resize_channels(img,nh,b0)
        new_img_h_const = resize_channels(img,h0,nb)

        fname = f"b_{r}_{filename}"
        cv.imwrite(os.path.join(output_dir,fname),new_img_b_const)
        fname = f"h_{r}_{filename}"
        cv.imwrite(os.path.join(output_dir,fname),new_img_h_const)
                       
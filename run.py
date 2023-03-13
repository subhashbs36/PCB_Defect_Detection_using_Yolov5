
import torch
from PIL import Image
import json
import cv2
from PyQt5 import QtCore, QtWidgets, uic, QtWidgets
from actions import ImageViewer
import sys, os, shutil
import time
import sys
import numpy as np
from PIL import Image



Image.MAX_IMAGE_PIXELS = None
img_data = {}


#---------Load Image----------------------------------------

gui = uic.loadUiType("main.ui")[0]     # load UI file designed in Qt Designer
VALID_FORMAT = ('.BMP', '.GIF', '.JPG', '.JPEG', '.PNG', '.PBM', '.PGM', '.PPM', '.TIFF', '.XBM')  # Image formats supported by Qt

def getImages(folder):
    ''' Get the names and paths of all the images in a directory. '''
    image_list = []
    if os.path.isdir(folder):
        for file in os.listdir(folder):
            if file.upper().endswith(VALID_FORMAT):
                im_path = os.path.join(folder, file)
                image_obj = {'name': file, 'path': im_path }
                image_list.append(image_obj)
    return image_list

#-------------------------------------------------------------------

processed_img_folder = 'output_images'
weight_loc = 'model/best.pt'
image_source = 'input_images'
thresh = 0.7

#-----------------------MainWindow----------------------------------

class Iwindow(QtWidgets.QMainWindow, gui):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.cntr, self.numImages = -1, -1  # self.cntr have the info of which image is selected/displayed
        self.image_viewer = ImageViewer(self.qlabel_image)
        self.image_viewer2 = ImageViewer(self.orig_img)
        self.showMaximized()
        self.setup()
        # self.selectDir()

    #------------Setup-----------------

    def setup(self):
        self.progressBar1.hide()
        self.__connectEvents()
        self.diable_btns()

    def folder_managment(self):
        try:
            shutil.rmtree(processed_img_folder)
            os.mkdir(processed_img_folder)
        except:
            pass


    #------------------Handel Buttons---------------------

    #----------------------------------------

    def After_run(self):
        self.enable_btn()
        self.selectDir()
        print(img_data)
        # self.Start_process.setEnabled(False)


    def diable_btns(self):
        self.next_im.setEnabled(False)
        self.prev_im.setEnabled(False)
        self.prev_im.setEnabled(False)
        self.zoom_plus.setEnabled(False)
        self.zoom_minus.setEnabled(False)
        self.reset_zoom.setEnabled(False)
        self.toggle_line.setEnabled(False)
        self.toggle_rect.setEnabled(False)
        self.refresh.setEnabled(False)
        self.undo.setEnabled(False)
        self.redo.setEnabled(False)

    def enable_btn(self):
        self.next_im.setEnabled(True)
        self.prev_im.setEnabled(True)
        self.prev_im.setEnabled(True)
        self.zoom_plus.setEnabled(True)
        self.zoom_minus.setEnabled(True)
        self.reset_zoom.setEnabled(True)
        self.toggle_line.setEnabled(True)
        self.toggle_rect.setEnabled(True)
        self.refresh.setEnabled(True)
        self.undo.setEnabled(True)
        self.redo.setEnabled(True)

    def __connectEvents(self):
        try:
            # self.open_folder.clicked.connect(self.selectDir)
            self.next_im.clicked.connect(lambda: self.nextImg())
            self.prev_im.clicked.connect(lambda: self.prevImg())
            self.qlist_images.itemClicked.connect(self.item_click)
            # self.save_im.clicked.connect(self.saveImg)

            self.zoom_plus.clicked.connect(lambda: self.image_viewer.zoomPlus())
            self.zoom_minus.clicked.connect(lambda: self.image_viewer.zoomMinus())
            self.reset_zoom.clicked.connect(lambda: self.image_viewer.resetZoom())

            self.toggle_line.toggled.connect(lambda: self.action_line())
            self.toggle_rect.toggled.connect(lambda: self.action_rect())
            self.Start_process.clicked.connect(lambda: self.run())
            self.refresh.clicked.connect(lambda: self.selectDir())
        except:
            pass

    def set_image_Textdata(self, img_addr):
        name = os.path.split(img_addr)
        # img_dic = dict((key, val) for (key, val) in img_data)
        self.set_comprehensive_data(img_data)
        img_val = img_data[name[1]]
        
        no_instances = len(img_val)
        res = []
        for i in img_val:
            val = i['name']
            if val not in res:
                res.append(val)
        names =''
        for i in res:
            names += '\n'+i
        info = f"Detected Defects: {names} \n\nNumber of Defects: {no_instances}"
        self.img_Data.setText(info)

    def set_comprehensive_data(self, img_dic):
        total_inst = 0
        for i in img_dic.values():
            total_inst += len(i)
        res = []
        for i in img_dic.values():
            for j in i:
                val = j['name']
                if val not in res:
                    res.append(val)
        class_size = len(res)
        # print(res)
        names =''
        for i in res:
            names += '\n'+i+' '
        info = f"Total Type Detected: {class_size} \n\nDetected Defects Types: {names} \n\nTotal Defects: {total_inst}"
        self.final_data.setText(info)
        pass
    
    def clear_screen(self):
        self.qlist_images.clear()
        self.img_Data.clear()
        self.final_data.clear()
        self.qlabel_image.clear()

    def selectDir(self):
        ''' Select a directory, make list of images in it and display the first image in the list. '''
        # open 'select folder' dialog box
        self.qlist_images.clear()
        self.folder = processed_img_folder
        if not self.folder:
            QtWidgets.QMessageBox.warning(self, 'No Folder Selected', 'Please select a valid Folder')
            return
        
        self.logs = getImages(self.folder)
        self.numImages = len(self.logs)

        # make qitems of the image names
        self.items = [QtWidgets.QListWidgetItem(log['name']) for log in self.logs]
        for item in self.items:
            self.qlist_images.addItem(item)

        # display first image and enable Pan 
        self.cntr = 0
        self.image_viewer.enablePan(True)
        
        self.image_viewer.loadImage(self.logs[self.cntr]['path'])
        self.setOrigImage(self.logs[self.cntr]['path'])
        self.items[self.cntr].setSelected(True)
        self.set_image_Textdata(self.logs[self.cntr]['path'])
        
        # QtWidgets.QMessageBox.warning(self, 'Sorry', 'No Images! in the destination')
        #self.qlist_images.setItemSelected(self.items[self.cntr], True)

        # enable the next image button on the gui if multiple images are loaded
        if self.numImages > 1:
            self.next_im.setEnabled(True)

    def setOrigImage(self, img):
        name = os.path.split(img)[1]
        loc = f'{image_source}/{name}'
        self.image_viewer2.loadImage2(loc)

    def resizeEvent(self, evt):
        if self.cntr >= 0:
            self.image_viewer.onResize()

    def nextImg(self):
        if self.cntr < self.numImages -1:
            self.cntr += 1
            self.image_viewer.loadImage(self.logs[self.cntr]['path'])
            self.items[self.cntr].setSelected(True)
            self.set_image_Textdata(self.logs[self.cntr]['path'])
            self.setOrigImage(self.logs[self.cntr]['path'])
            # print(self.logs[self.cntr]['path'])
            #self.qlist_images.setItemSelected(self.items[self.cntr], True)
        else:
            QtWidgets.QMessageBox.warning(self, 'Sorry', 'No more Images!')

    def prevImg(self):
        if self.cntr > 0:
            self.cntr -= 1
            self.image_viewer.loadImage(self.logs[self.cntr]['path'])
            self.items[self.cntr].setSelected(True)
            self.set_image_Textdata(self.logs[self.cntr]['path'])
            self.setOrigImage(self.logs[self.cntr]['path'])
            # self.qlist_images.setItemSelected(self.items[self.cntr], True)
        else:
            QtWidgets.QMessageBox.warning(self, 'Sorry', 'No previous Image!')

    def item_click(self, item):
        self.cntr = self.items.index(item)
        self.image_viewer.loadImage(self.logs[self.cntr]['path'])
        self.setOrigImage(self.logs[self.cntr]['path'])
        self.set_image_Textdata(self.logs[self.cntr]['path'])

    def action_line(self):
        if self.toggle_line.isChecked():
            self.qlabel_image.setCursor(QtCore.Qt.CrossCursor)
            self.image_viewer.enablePan(False)

    def action_rect(self):
        if self.toggle_rect.isChecked():
            self.qlabel_image.setCursor(QtCore.Qt.CrossCursor)
            self.image_viewer.enablePan(False)

    def action_move(self):
        if self.toggle_move.isChecked():
            self.qlabel_image.setCursor(QtCore.Qt.OpenHandCursor)
            self.image_viewer.enablePan(True)


#-------------Model--------------------

    def img_directory(self, path):
        count = 0
        img_loc = []
        for dirname, dirs, files in os.walk(path):
            for filename in files:
                filename_without_extension, extension = os.path.splitext(filename)
                if extension.upper().endswith(VALID_FORMAT):
                    print('found image')
                    print(filename_without_extension)
                    count = count +1
                    print(f"count = {count}")
                    image_path = os.path.join(dirname, filename)
                    img_loc.append(image_path)

        return img_loc
    
    def run(self):
        self.clear_screen()
        self.folder_managment()
        self.progressBar1.show()
        ival = 0
        self.progressBar1.setValue(ival)
        for i in range(35):
            ival = i
            self.progressBar1.setValue(ival)
            time.sleep(0.03)
        img_loc = self.img_directory(image_source)
        global img_data
        count =0
        imgSize = ival+len(img_loc)
        for iimg_path in img_loc:
            try:
                model = self.get_yolov5()
                annotation = self.evaluate_img(model, iimg_path)
                load_img = self.plot_img(iimg_path, annotation)
                self.setOrigImage(iimg_path)
                self.image_viewer.loadImage(load_img)
                self.set_image_Textdata(load_img)
                count += 1
                print(count)
            except:
                pass

            for i in range(ival, imgSize):
                ival += 1
                self.progressBar1.setValue(i)
                time.sleep(0.03)
                break
        for i in range(ival,101):
            ival = i
            self.progressBar1.setValue(ival)
            time.sleep(0.03)
        self.progressBar1.hide()
        print("Model Process has been Ended!")
        self.After_run()



    ###############---Functions---###################

    def get_yolov5(self):
        # local best.pt
        model = torch.hub.load('./yolov5', 'custom', path=weight_loc, source='local')  # local repo
        model.conf = thresh
        return model


    def evaluate_img(self, model, input_image):
        name = os.path.split(input_image)[1]
        results = model(input_image)
        detect_res = results.pandas().xyxy[0].to_json(orient="records")  # JSON img1 predictions
        detect_res = json.loads(detect_res)
        img_data[name] = detect_res
        return {name: detect_res}


    def plot_img(self, img, result):
        name = os.path.split(img)[1]
        # Define colors for each class
        colors = {
            'open': (0, 255, 0),   # green
            'short': (255, 0, 0),  # blue
            'mousebite': (0, 0, 255), # red
            'spur': (255, 255, 0), # cyan
            'copper': (0, 255, 255), # yellow
            'pinhole': (155, 105, 205)
        }

        # Load the image
        image = cv2.imread(img)

        # Loop through each result and draw the bounding box on the image
        for r in result[name]:
            class_name = r['name']
            color = colors[class_name]
            xmin, ymin, xmax, ymax = map(int, [r['xmin'], r['ymin'], r['xmax'], r['ymax']])
            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, thickness=2)
            text = f"{class_name}"
            cv2.putText(image, text, (xmin, ymin-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        new_name = f'{processed_img_folder}/{name}'
        cv2.imwrite(new_name, image)
        return new_name




#-------------------main--------------------------------

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create("Cleanlooks"))
    app.setPalette(QtWidgets.QApplication.style().standardPalette())
    parentWindow = Iwindow(None)
    sys.exit(app.exec_())





if __name__ == "__main__":
    main()










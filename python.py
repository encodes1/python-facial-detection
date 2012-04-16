import web, sys, os, subprocess, uuid
from opencv.cv import *
from opencv.highgui import *
from shutil import copy
 
def detectObjects(image, imagefile):
  """Converts an image to grayscale and prints the locations of any
     faces found"""
  grayscale = cvCreateImage(cvSize(image.width, image.height), 8, 1)
  cvCvtColor(image, grayscale, CV_BGR2GRAY)
 
  storage = cvCreateMemStorage(0)
  cvClearMemStorage(storage)
  cvEqualizeHist(grayscale, grayscale)
  cascade = cvLoadHaarClassifierCascade(
    '/usr/share/doc/opencv-doc/examples/haarcascades/haarcascade_frontalface_alt.xml.gz',
    cvSize(1,1))
  faces = cvHaarDetectObjects(grayscale, cascade, storage, 1.2, 2,
                             CV_HAAR_DO_CANNY_PRUNING, cvSize(50,50))
 
  if faces.total > 0:
    for f in faces:
        print("found a face: [(%d,%d) -> (%d,%d)]" % (f.x, f.y, f.x+f.width, f.y+f.height))
        foundFace(imagefile, f)
  return faces.total
 
def foundFace(imagefile, f):
    #os.system("convert {image} -stroke red -fill transparent -draw \"rectangle {a},{b} {c},{d}\" {output}".format(
    #                image=imagefile,
    #                a=f.x+6,
    #                b=f.y,
    #                c=f.width,
    #                d=f.height,
    #                output=imagefile));
    print ("convert {image} -draw \"image SrcOver {a},{b} {c},{d} devil-horns.png\" {output}".format(
                    image=imagefile,
                    a=f.x+6,
                    b=f.y,
                    c=f.width,
                    d=f.height,
                    output=imagefile));
    os.system("convert {image} -draw \"image SrcOver {a},{b} {c},{d} devil-horns.png\" {output}".format(
                    image=imagefile,
                    a=f.x,
                    b=(f.y-(f.y/2)),
                    c=(f.width/1.2),
                    d=(f.height/2),
                    output=imagefile));
 
urls = (
    '/upload', 'Upload',
    '/Uploads/(.*)', 'Uploads' #this is where the image folder is located....
)
 
class Uploads:
    def GET(self,name):
        ext = name.split(".")[-1] # Gather extension

        cType = {
            "png":"images/png",
            "jpg":"image/jpeg",
            "gif":"image/gif",
            "ico":"image/x-icon"            }

        #if name in os.listdir('Uploads'):  # Security
        web.header("Content-Type", cType[ext]) # Set the Header
        return open('Uploads/%s'%name,"rb").read() # Notice 'rb' for reading images
        #else:
        #    raise web.notfound()

class Upload:
    def GET(self):
        web.header("Content-Type","text/html; charset=utf-8")
        return """<html><head><link rel="shortcut icon" href="/static/favicon.ico"
type="image/x-icon"></head><body>
<form method="POST" enctype="multipart/form-data" action="">
<input type="file" name="myfile" />
<br/>
<input type="submit" />
</form>
</body></html>"""
    def POST(self):
        x = web.input(myfile={})
        filedir = '/home/mtooth/Projects/pyface/Uploads' # change this to the directory you want to store the file in.
        if 'myfile' in x: # to check if the file-object is created
	   
            filepath=x.myfile.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
            #filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
            filename = str(uuid.uuid4())
 	    
            fout = open(filedir +'/'+ filename,'w') # creates the file where the uploaded file should be stored
            fout.write(x.myfile.file.read()) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete.
            # detect face
            imagefile = filedir +'/'+ filename;
            image = cvLoadImage(imagefile);
            unique_name = str(uuid.uuid4())
	    print(unique_name)
            output_path = '/home/mtooth/Projects/pyface/Uploads/%s.png' % unique_name
            if (detectObjects(image, imagefile) > 0):
                copy(imagefile, output_path)
                raise web.seeother("Uploads/%s.png" % unique_name)
            else:
                return """No face found."""
        raise web.seeother('/upload')
 
if __name__ == "__main__":
   app = web.application(urls, globals(), True)
   app.run()

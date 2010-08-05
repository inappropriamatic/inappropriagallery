import dircache
import sys
from random import sample
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.web.static import File
from tumblrpost import TumblrPost
from galleryhelper import html_header, html_footer, local_jquery

""" Makes a gallery running on localhost:8014 using a directory of images
    Those images can be then uploaded to Tumblr.
    
    Argument 1:  The directory of images you want to view
    Argument 2:  The number of images you want to display"""


# get the image directory
image_directory = sys.argv[1]

if image_directory[-1] != '/':
    image_directory += '/'

num_images = int(sys.argv[2])

# for logging in.  Unsecure, but whatever.
email = None
password = None

if len(sys.argv) == 5:
    email = sys.argv[3]
    password = sys.argv[4]



class GallerySite(Resource):
    def render_GET(self, request):
        request.setResponseCode(200)
        html = html_header
          
        chosen = sample(dircache.listdir(image_directory), num_images)
        for image in chosen:
            html += "\n<div class=\"img\" id=\"" + image + "\"><img src=\"" + image + "\" class=\"scaled\"></div><br /><br />"
            root.putChild(image, File(image_directory + image)) 
          
        html += html_footer
          
        return html
    
    def render_POST(self, request):
        global email
        global password
        global image_directory
        tp = TumblrPost(email, password)
        tp.set_caption( request.args["caption"][0] )
        tp.set_state( request.args["qp"][0] )
        tp.set_upload_file( image_directory + request.args["img_name"][0] )
        
        if tp.connect_and_post():
            return """<h1>Success</h1><a href="/">Return to gallery</a>"""
        else:
            return """
            <html><head></head><body>
            <h1 style="font-size:500%">FAIL</h1>
            <a href="/">Return to gallery</a>
            </body></html>"""



class LoginSite(Resource):
    def render_GET(self, request):
        return """<html><head></head><body>
                <h1>Login to Tumblr</h1><br>
                <form method="POST"><table>
                <tr><td>Email address:</td><td> <input type="text" name="usr" /></td></tr>
                <tr><td>Password:</td><td> <input type="password" name="pwd" /></td></tr>
                <tr><td><input type="submit"></td><td></td></tr> 
                </form></body></html>"""
        
    def render_POST(self, request):
        global email
        global password
        
        email = request.args["usr"]
        password = request.args["pwd"]
        
        return """<html><head></head><body>
        <h1>Login Successful!</h1><small> probably.</small><br /><br /><br />
        <a href="/">Return to gallery</a>
        </body></html>"""
        



# make the root of the directory.
root = Resource()
root.putChild("", GallerySite())  # add the gallery and login pages
root.putChild("login", LoginSite() )
if local_jquery:
    root.putChild("jquery.js", File("jquery.js"))
factory = Site(root)
reactor.listenTCP(8014, factory)  # start it running on port 8014
reactor.run()




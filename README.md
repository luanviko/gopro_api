# gopro_api

This is a tiny REST-like API to capture and download photos from a GoPro Hero 10 camera. 
It uses python's requests package to ```"GET"``` data from the endpoints defined by the GoPro's official HTTP documentation.

Pydantic's base model is used to validate endpoints' URLs, media's directories and destination folder.

## Methods and Endpoints

The following is a brief description of the GoPro's class methods and the endpoints it access to retrieve information.
While ```10.5.5.8:8080``` is the default ip:port address, 
the class allows for it to be changed.

### GoPro.state() 

Description: Retrieve the integers and strings for status and settings in the ```state``` dictionary. Basic information about camera operation.

Endpoint: http://10.5.5.9:8080/gopro/camera/state


### GoPro.capture_photo()

Description: Change the shutter state to 1. If in photo mode, will take a single photo. If in video mode, will start video capture. **Only use in photo mode.**

Endpoint: http://10.5.5.9:8080/camera/shutter/start


### GoPro.download()

Description: Retrive the information in Media.url (endpoint containing file in camera's SD card) and save it into Media.save_dir folder (computer's permanent memory). 

Endpoint example: http://10.5.5.9:8080/videos/DCIM/directory/filename 


### GoPro.download_all() 

Description: Retrive list of all files in SD card of the camera and download all with GoPro.download()

Endpoint: http://10.5.5.9:8080/gopro/media/list


### GoPro.download_last()
 
Description: Retrive list of all files in SD card of the camera and download the most recent with GoPro.download()

Endpoint: http://10.5.5.9:8080/gopro/media/list


### GoPro.wait() 

Description: Access the list of media store in the SD drive continuously, until the list is ready to be retrived.

Endpoint: http://10.5.5.9:8080/gopro/media/list




## Media Class

Contains ```url``` and ```save_dir``` variables, which respectively describe the endpoint/ directory in the camera's SD card and the destination folder in the computer.

The GoPro's api only accepts the 'HTTP' (not 'HTTPS') protocol, so ```url``` is validated as such. In turn, ```save_dir```'s validation requires the folder to exist and creates the path if it does not.

Usage:




## Example

Manually put camera in photo mode.

Then, the following excerpt from ```capture_photo.py``` illustrates the photo-capture procedure.

```python
gopro = GoPro(debug = debug)
gopro.capture_photo()
ready = gopro.wait()
if ready:
    gopro.download_last(save_dir = Path('./photos'))  
```

## Known Issues

To ascertain the state of the camera (busy, idle, etc), you are supposed to read the respective integers in the ```state['status']``` dictionary. Unfortunately, the integer for busy is always '0', even when the camera is not available. Hence, the ```GoPro.wait()``` method tries to retrive the media list until it becomes available, rather than reading the ```busy``` integer.
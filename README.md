# gopro_api

This is a tiny REST-like API to capture and download photos from a GoPro Hero 10 camera. 
It uses python's requests package to ```"GET"``` data from the endpoints defined by the GoPro's official HTTP documentation.

Pydantic's base model is used to validate endpoints' URLs, media's directories and destination folder.

## GoPro Methods and Respective Endpoints

### GoPro.state() 
http://10.5.5.9:8080/gopro/camera/state'

### GoPro.info()
http://10.5.5.9:8080/gp/gpControl'

### GoPro.capture_photo()
http://10.5.5.9:8080/camera/shutter/start

### GoPro.wait() 
http://10.5.5.9:8080/gopro/media/list'

### GoPro.download(), GoPro.download_all() and GoPro.download_last()



## Media Class

Contains ```url``` and ```save_dir``` variables, which respectively describe the endpoint/ directory in the camera's SD card and the destination folder in the computer.

The GoPro's api only accepts the 'HTTP' (not 'HTTPS') protocol, so ```url``` is validated as such. In turn, ```save_dir```'s validation requires the folder to exist and creates the path if it does not.

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
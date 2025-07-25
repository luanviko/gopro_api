from pydantic import BaseModel, HttpUrl, field_validator
from typing import Any, Dict
import requests, json, time, sys, warnings
from requests import Response
from pathlib import Path

class Media(BaseModel):

    url : HttpUrl
    save_dir : Path

    @field_validator("url")
    def ensure_url_integrity(cls, v):
        if not v.startwitch("http://"):
            raise ValueError("Only HTTP protocol allowed.")
        return v 

    @field_validator("save_dir")
    def ensure_save_dir_integrity(cls, v):
        os.makedirs(save_dir, exist_ok = True)


class GoPro(BaseModel):
    gopro_ip: str = '10.5.5.9:8080'
    base_url: str = f'http://{gopro_ip}/gopro'
    debug: bool = False

    @field_validator("base_url")
    def ensure_url_integrity(cls, v):
        if not v.startwitch("http://"):
            raise ValueError("Only HTTP protocol allowed.")
        return v 

    def state(self) -> Dict[str, Any]:
        """Get the current state of the GoPro camera.

        Returns:
            Dict[str, Any]: JSON response containing the camera state.
        """
        url = f'{self.base_url}/camera/state'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def capture_photo(self) -> Response:
        """Trigger the GoPro to capture a photo.

        Returns:
            Response: The HTTP response from the camera.
        """
        url = f'{self.base_url}/camera/shutter/start'
        response = requests.get(url)
        response.raise_for_status()
        return response

    def download(self, media: Media) -> None:
        """Download a specific media file from the GoPro.

        Args:
            directory (str): Directory where the file is located.
            name (str): Filename to download.
        """
        response = requests.get(media.url)

        if response.status_code == 200:
            print(f'Copying: {name}.')
            with open(f'./photos/{name}', 'wb') as photo:
                photo.write(response.content)
        
        return None

    def download_all(self, save_dir: Path = Path('./photos')) -> None:
        """Download all media files from the GoPro."""
        url = f'{self.base_url}/media/list'
        response = requests.get(url)
        response.raise_for_status()

        media = response.json()['media'][0]
        directory = media['d']
        files = media['fs']

        if self.debug:
            with open("response.json", "w") as f:
                json.dump(response.json(), f, indent=2)
            print(directory)
            print('No. of files:', len(files))

        for file in files:
            task = Media(
                url = f'http://{self.gopro_ip}/videos/DCIM/{directory}/{file['n']}',
                save_dir = save_dir
            )
            self.download(directory, task)

        return None

    def download_last(self, save_dir: Path = Path('./photos')) -> None:
        """Download the most recently captured media file."""
        url = f'{self.base_url}/media/list'
        response = requests.get(url)
        response.raise_for_status()

        media = response.json()['media'][0]
        directory = media['d']
        files = media['fs']
        sorted_files = sorted(files, key=lambda f: f['cre'])
        last_file = sorted_files[-1]['n']

        task = Media(
            url = f'http://{self.gopro_ip}/videos/DCIM/{directory}/{last_file}',
            save_dir = save_dir
        )
        self.download(directory, last_file)

        return None

    def wait(self, poll_interval:float = 0.5, timeout: int = 5) -> bool:
        """Poll the media list endpoint until it responds without 
           error or timeout occurs.

        Args:
            poll_interval (float): Seconds between requests.
            timeout (int): Maximum seconds to wait.

        Returns:
            bool: True if media list became available, False on timeout.
        """
        start = time.time()

        while True:
            
            try:
                url = f'{self.base_url}/media/list'
                response = requests.get(url)
                response.raise_for_status()
                print(response)
                return True

            except requests.exceptions.HTTPError as e:
                if self.debug:
                    warnings.warn(f"HTTPError: {e}", RuntimeWarning)

            else:
                raise

            if time.time() - start > timeout:  
                if self.debug:
                    warnings.warn("Timeout waiting for media list availability.", RuntimeWarning)
                return False

            time.sleep(poll_interval)

        return True


def main():

    debug = True
    gopro = GoPro(debug = debug)

    if debug:
        status = gopro.state()['status']
        info   = gopro.info()
        print(status, info)

    gopro.capture_photo()
    ready = gopro.wait()
    if ready:
        gopro.download_last(save_dir = Path('./photos'))    
    

if __name__ == '__main__':
    main()
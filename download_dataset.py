import os
import zipfile
import requests
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()


class DownloadDataset:
    def __init__(
        self,
        url: str,
        download_dir: str,
        dataset_name: str,
    ):
        self.url = url
        self.download_dir = Path(download_dir)
        self.dataset_name = dataset_name

        # Ensure directories exist
        self.download_dir.mkdir(parents=True, exist_ok=True)

        # Construct file name automatically from URL or use a fixed name
        self.download_path = self.download_dir / self.dataset_name
        self.expected_size = None

    def download(self) -> str:
        if self.download_path.exists():
            print(f"[INFO] Dataset already exists at {self.download_path}")
            return str(self.download_path)

        print(f"[INFO] Downloading dataset from {self.url} ...")
        try:
            response = requests.get(self.url, stream=True)
            self.expected_size = int(response.headers.get("content-length", 0))
            response.raise_for_status()

            with open(self.download_path, "wb") as f, tqdm(
                total=self.expected_size, unit="iB", unit_scale=True, desc="Downloading"
            ) as t:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        t.update(len(chunk))

            print(f"[INFO] Dataset downloaded successfully at {self.download_path}")
            return str(self.download_path)

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to download dataset: {e}")
            raise

    def verify_file(self, expected_size: int = 0) -> bool:
        if not self.download_path.exists():
            print("[ERROR] File does not exist.")
            return False

        if expected_size is None:
            expected_size = self.expected_size

        if expected_size:
            actual_size = self.download_path.stat().st_size
            if actual_size != expected_size:
                print(
                    f"[ERROR] File size mismatch: expected {expected_size}, got {actual_size}"
                )
                return False

        print("[INFO] File verification passed.")
        return True

    def unzip_dataset(self) -> bool:
        if zipfile.is_zipfile(self.download_path):
            print("[INFO] Downloaded file is Zip now Unzip!!")
            extract_to = self.download_path.with_suffix("")  # ./datasets/file
            with zipfile.ZipFile(self.download_path, "r") as zip_file:
                zip_file.extractall(extract_to)
        else:
            print("[INFO] Downloaded file is Zip")
        return True


if __name__ == "__main__":
    url = str(os.getenv("DATASET_URL"))
    download_dir = "./datasets"  # Folder where .zip will be stored
    dataset_name = "cat.zip"

    downloader = DownloadDataset(
        url=url, download_dir=download_dir, dataset_name=dataset_name
    )
    downloader.download()
    downloader.verify_file()
    downloader.unzip_dataset()

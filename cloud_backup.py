from datetime import datetime
import io
import boto3
from tqdm import tqdm


class ProgressBytesIO(io.BytesIO):
    def __init__(self, bytes_io, progress_bar):
        self._bytes_io = bytes_io
        self._progress_bar = progress_bar
        super().__init__(bytes_io)

    def read(self, size=-1):
        chunk = super().read(size)
        self._progress_bar.update(len(chunk))
        return chunk


def backup_db(
    db_name: str,
    bucket_name: str,
    endpoint_url: str,
    access_key_id: str,
    access_key_secret: str,
    region_name: str,
):
    s3 = boto3.client(
        service_name="s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=access_key_secret,
        region_name=region_name,
    )

    with open(db_name, "rb") as db:
        file_content = db.read()

    file_size = len(file_content)
    file_name = f"{db_name.split('.')[0]}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.db"

    print(f"backing up {db_name} to bucket {bucket_name} as {file_name}")
    print("initial file progress will stall as the initial connection is established")
    with tqdm(total=file_size, unit="B", unit_scale=True, desc=file_name) as progress_bar:
        progress_bytes_io = ProgressBytesIO(file_content, progress_bar)
        s3.upload_fileobj(progress_bytes_io, bucket_name, file_name)

    print("backup complete")

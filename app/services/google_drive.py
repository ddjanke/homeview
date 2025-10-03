import os
from googleapiclient.discovery import build
from .auth import GoogleAuthService
from config import Config


class GoogleDriveService:
    def __init__(self):
        self.auth_service = GoogleAuthService()
        self.service = None
        self.icons_folder_id = None
        self._initialize_service()

    def _initialize_service(self):
        """Initialize the Google Drive service."""
        try:
            creds = self.auth_service.get_credentials()
            self.service = build("drive", "v3", credentials=creds)
            # Get the icons folder ID from config
            self.icons_folder_id = Config.GOOGLE_DRIVE_ICONS_FOLDER_ID
        except Exception as e:
            print(f"Error initializing Google Drive service: {e}")
            self.service = None

    def list_icons(self):
        """List all icon files in the Google Drive icons folder."""
        if not self.service or not self.icons_folder_id:
            return []

        try:
            # Query for files in the icons folder
            query = (
                f"'{self.icons_folder_id}' in parents and mimeType contains 'image/'"
            )

            results = (
                self.service.files()
                .list(
                    q=query,
                    fields="files(id,name,mimeType,webContentLink)",
                    orderBy="name",
                )
                .execute()
            )

            files = results.get("files", [])

            # Process files to create a mapping of name to file info
            return {
                os.path.splitext(file["name"])[0].lower(): {
                    "id": file["id"],
                    "name": file["name"],
                    "url": file["webContentLink"],
                    "mime_type": file["mimeType"],
                }
                for file in files
            }

        except Exception as e:
            print(f"Error listing icons: {e}")
            return {}

    def download_icon(self, file_id, save_path):
        """Download an icon file to local storage."""
        if not self.service or not file_id:
            return False

        try:
            # Get file content
            request = self.service.files().get_media(fileId=file_id)

            # Download the file
            with open(save_path, "wb") as f:
                f.write(request.execute())

            return True

        except Exception as e:
            print(f"Error downloading icon {file_id}: {e}")
            return False

    def sync_icons_to_local(self, local_icons_dir):
        """Download icons from Google Drive folder to local directory, skipping existing files."""
        if not self.service or not self.icons_folder_id:
            return False

        try:
            # Create local icons directory if it doesn't exist
            os.makedirs(local_icons_dir, exist_ok=True)

            # Get all icons from the folder
            icons = self.list_icons()

            if not icons:
                print("No icons found in Google Drive folder")
                return False

            downloaded_count = 0
            skipped_count = 0
            for icon_info in icons.values():
                file_id = icon_info["id"]
                original_name = icon_info["name"]
                local_path = os.path.join(local_icons_dir, original_name)

                # Skip if file already exists
                if os.path.exists(local_path):
                    skipped_count += 1
                    continue

                if self.download_icon(file_id, local_path):
                    downloaded_count += 1
                    print(f"Downloaded: {original_name}")
                else:
                    print(f"Failed to download: {original_name}")

            if downloaded_count > 0:
                print(
                    f"Successfully downloaded {downloaded_count} icons to {local_icons_dir}"
                )
            if skipped_count > 0:
                print(f"Skipped {skipped_count} existing icons")
            return True

        except Exception as e:
            print(f"Error syncing icons: {e}")
            return False

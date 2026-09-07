import os
import boto3

class r2Storage:

	def __init__(self):

		self.__account_id = os.getenv("CLOUDE_FARE_ACCOUNT_ID", "").strip()
		self.__access_key = os.getenv("CLOUDE_FARE_ACCESS_KEY_ID", "").strip()
		self.__secret_access_key = os.getenv("CLOUDE_FARE_SECRET_ACCESS_KEY", "").strip()
		self.__bucket_name = os.getenv("CLOUDE_FARE_BUCKET_NAME", "").strip()

		self.r2 = boto3.client(
			"s3",
			endpoint_url=f"https://{self.__account_id}.r2.cloudflarestorage.com",
			aws_access_key_id=self.__access_key,
			aws_secret_access_key=self.__secret_access_key,
			region_name="auto",
		)


	def list_objects(self, folder_name:str|None = None) -> list[dict]:

		response = self.r2.list_objects_v2(
			Bucket=self.__bucket_name,
			Prefix=f"{folder_name}/" if folder_name else None
		)

		return response.get("Contents", [])
		 

	def upload_files(self, local_path, file_path_in_server):

		with open(local_path, "rb") as fo:
			self.r2.upload_fileobj(
				fo,
				self.__bucket_name,
				file_path_in_server
			)

	def download_files(self, file_path_in_server, local_path):

		self.r2.download_file(
            self.__bucket_name,
            file_path_in_server,
            local_path
        )

	def create_folders(self, folder_name):

		self.r2.put_object(
			Bucket=self.__bucket_name,
			Key=f"{folder_name}/"
		)

		 
if __name__ == '__main__':
	pass
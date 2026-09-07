import requests, yaml
import os, shutil
from datetime import datetime, timezone

#local modules

import cloudeflare
import github_file_actions

class WhatsappBOT:

    def __init__(self):

        self.cloudeflare = cloudeflare.r2Storage()

        self.__github_token = os.getenv("TOKEN_GITHUB", "").strip()
        self.__github_username = os.getenv("USERNAME_GITHUB", "").strip()
        self.__github_repo_name = os.getenv("REPO_NAME_GITHUB", "").strip()

        self.__token = os.getenv("WHAPI_TOKEN", "").strip()
        self.__receiver_number = os.getenv("MY_NUMBER", "").strip()

        self.__client_number = os.getenv("CLIENT_NUMBER", "").strip()
        self.__sister_number = os.getenv("SISTER_NUMBER", "").strip()
        self.__father_number = os.getenv("FATHER_NUMBER", "").strip()
        self.__mother_number = os.getenv("MOTHER_NUMBER", "").strip()

        self.__folder_dict = {
            self.__client_number:"client",
            self.__sister_number:"sister",
            self.__father_number:"father",
            self.__mother_number:"mother"
        }

        self.__numbers_list = self.__folder_dict.keys()

        self.download_config_file_from_github()

        self.__pre_built_folders()

    def download_config_file_from_github(self):

        # download the config file from github to check the created folders (or) configaration

        branch = "main"

        url = f"https://raw.githubusercontent.com/{self.__github_username}/{self.__github_repo_name}/{branch}/config.yaml"

        github_file_actions.download_file_from_github(github_token=self.__github_token,
                                                      url=url,
                                                      file_name="config.yaml")

        shutil.copyfile("./config.yaml", "./config-duplicate.yaml") # copying config file for comparing at the last

    def upload_config_file_to_github(self):

        # uplodes the updated config file to github

        branch = "main"
        file_path = "./config.yaml"

        url = f"https://api.github.com/repos/{self.__github_username}/{self.__github_repo_name}/contents/{file_path}"

        github_file_actions.upload_file_to_github(github_token=self.__github_token,
                                                  url=url,
                                                  branch=branch,
                                                  file_path=file_path,
                                                  message="new profile pic updated")


    def __pre_built_folders(self):

        folders_need_to_create= []
        available_folders = []

        with open("./config.yaml", "r") as fo:
            data = yaml.safe_load(fo) or {}

        mapping_data:list = data.setdefault("map", [])
        
        available_folders = [d.get("folder-name") for d in mapping_data if mapping_data]

        for name in self.__folder_dict.values():

            if name not in available_folders:
                folders_need_to_create.append(name)

        if folders_need_to_create:

            for folder_name in folders_need_to_create:

                self.cloudeflare.create_folders(f"{folder_name}/images") # create folder in cloudeflare bucket

                mapping_data.append({"folder-name": folder_name, "has-current-image":False}) # update the config data

            with open('./config.yaml', 'w') as fo: # updation of config file
                yaml.safe_dump(data, fo, sort_keys=False)

    def get_curent_time_in_timestamp(self) -> str:

        try:
            return str(int(datetime.now(timezone.utc).timestamp()))
        except Exception as e:
            return str(e)

    def __download_dp(self, number: str):

        url = f"https://gate.whapi.cloud/contacts/{number}/profile" # whapi url for profil pics 

        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {self.__token}"
        }

        response = requests.get(url, headers=headers)

        dp_url = response.json()["icon_full"]

        folder_name = self.__folder_dict[number] # gives the current folder name
        if dp_url and self.__check_dp_image_and_save(url=dp_url, folder_name=folder_name):
            # if we have dp image url and new dp then we will send the message
            self.__send_message(folder_name)
        
    def __check_dp_image_and_save(self, url:str, folder_name:str) -> bool:

        # compares the current image with avilable image if changed then we uplod the file to bucket

        with open('./config.yaml', 'r') as fo:
            yaml_data = yaml.safe_load(fo)

        r = requests.get(url)
        data = r.content

        curr_server_folder = folder_name
        curr_server_img_path = f"{curr_server_folder}/current.png"

        local_curr = "current.png" # local
        local_new = "new.png" # local

        with open(local_new, 'wb') as fo:
            fo.write(data)


        for d in yaml_data["map"]:
                
            if d.get("folder-name") == folder_name and not d.get("has-current-image"): 

                # if the dp is not availabe in previous and if it is avilable now we directly upload to the bucket
                # as current image and as well as in images folder collection
            
                with open(local_curr, 'wb') as fo:
                    fo.write(data)

                self.cloudeflare.upload_files(local_path=local_curr,
                                              file_path_in_server=curr_server_img_path)
                
                new_dp_path_server = f"{curr_server_folder}/images/{self.get_curent_time_in_timestamp()}.png"
                
                self.cloudeflare.upload_files(local_path=local_new,
                                              file_path_in_server=new_dp_path_server)
                
                d["has-current-image"] = True

                with open("./config.yaml", 'w') as fo:
                    yaml.safe_dump(yaml_data, fo, sort_keys=False)

                return True

            elif d.get("folder-name") == folder_name and d.get("has-current-image"):   
            
                self.cloudeflare.download_files(file_path_in_server=curr_server_img_path,
                                                local_path=local_curr)

        # checking
        
        with open(local_curr, 'rb') as fo:
            file1_data = fo.read()

        with open(local_new, 'rb') as fo:
            file2_data = fo.read()

        if file1_data == file2_data: # comparing curr available with newly downloaded one
            return False

        # if file data is mis match we need to save the image
        new_dp_path_server = f"{curr_server_folder}/images/{self.get_curent_time_in_timestamp()}.png"

        self.cloudeflare.upload_files(local_path=local_new,
                                      file_path_in_server=new_dp_path_server)
        
        self.cloudeflare.upload_files(local_path=local_new,
                                      file_path_in_server=f"{curr_server_folder}/current.png")

        return True

    def __send_message(self, folder_name) -> bool:

        # if you have any new dp we will send the message to whatsapp

        url = "https://gate.whapi.cloud/messages/text"

        message = f"we have a new dp for the {folder_name} profile"
        payload = {
            "typing_time": 0,
            "to": self.__receiver_number,
            "body": message
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.__token}"
        }

        response = requests.post(url, json=payload, headers=headers)

        return response.json()["sent"]

    def loop(self):

        for number in self.__numbers_list:
            self.__download_dp(number)
        
        with open("./config.yaml", "r") as fo:
            data1 = yaml.safe_load(fo)

        with open("./config-duplicate.yaml", "r") as fo:
            data2 = yaml.safe_load(fo)

        if data1 != data2: # compare yaml files data if any change update to github
            self.upload_config_file_to_github()

if __name__ == "__main__":
    w = WhatsappBOT()
    w.loop()


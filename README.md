<h1 style="text-align:center"> This is whatsapp DP dowloader BOT </h1>

### WORK FLOW 
- first it download the **config.yaml** file from github and make a copy
- it use the **config.yaml** file for checking the available folder and not available folders
- if any folders need to create it will create folder in **cloude flare r2 stoarage**.
- loops through the each number we provided
- if it is the first time check it download the dp and upload directly to the storage in current image and in images folder.
- else download the dp of whatsapp then check with the currently available image 
  if it is different then we will uploade the image to the images folder and update the current image
- if previously dp is not available and now if it is available then we update the has-current-image field to true in the    config file.
- at last we compare the **config.yaml** and copied file. if changed we upload **config.yaml** to the github
- we run this for every 4 hours in github workflows

---

### new mobile number addition
- if you want to check the new mobile number dp
- create a key, value pair in `.env` file
- then update your code like below 

``` python
self.__mother_number = os.getenv("MOTHER_NUMBER", "").strip() # load new mobile number

self.__folder_dict = {
    self.__client_number:"client", # already available

    self.__mother_number:"mother" # folder name that will be created in server
}
```

- add the same `.env` variables into github secrets
- update the github workflow yaml file
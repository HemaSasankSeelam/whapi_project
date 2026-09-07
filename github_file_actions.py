import requests
import base64

def download_file_from_github(github_token, url, file_name):
    
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    with open(f"./{file_name}", "wb") as file:
        file.write(response.content)

def upload_file_to_github(github_token, url, branch, file_path, message):

        # reads the file from local
        with open(file_path, "rb") as file:
            content = base64.b64encode(file.read()).decode("utf-8")

        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
        }

        # Get existing file SHA
        response = requests.get(
            url,
            headers=headers,
            params={"ref": branch}
        )

        sha = None

        if response.status_code == 200:
            sha = response.json()["sha"]
        elif response.status_code != 404:
            response.raise_for_status()

        # Upload/update file
        payload = {
            "message": message,
            "content": content,
            "branch": branch,
        }

        if sha:
            payload["sha"] = sha

        response = requests.put(
            url,
            headers=headers,
            json=payload
        )

        response.raise_for_status()
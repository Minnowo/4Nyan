import requests


def main():

    with requests.Session() as session:

        headers = {"Content-Type": "multipart/form-data"}

        payload = {"username": "this_is_as_username", "password": "super_strong_password"}

        request = session.post("http://localhost:721/auth/token", data=payload, headers=headers)

        print(request.text)


if __name__ == "__main__":
    main()

from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientBadRequestError
import logging, requests, sys
from dotenv import dotenv_values
from requests.exceptions import RetryError

config = dotenv_values(".env")

USERNAME = config['USERNAME']
PASSWORD = config['PASSWORD']

logger = logging.getLogger()

def following(client, user_name, limit: int = 100):
    res = {}
    user_id = client.user_id_from_username(user_name)
    try:
        print(f"Trying using user_following_v1({user_id}, {limit})...\n")
        res = client.user_following_v1(user_id, amount = limit)
    except (ClientBadRequestError, requests.HTTPError) as exception:
        try:
            print(f"Bad request while getting {user_name}:\n{exception}\n\n")
            print(f"Trying via user_following_gql({user_name}, {limit}) method...\n")
            res = client.user_following_gql(user_id, amount = limit)
        except (RetryError, Exception) as retry_error:
            print(f"Retry error while getting requesting via user_following_gql() {user_name}:\n{retry_error}\n\n")
            try:
                print(f"Trying again using user_following({user_id}, {limit}) method...\n")
                res = client.user_following(user_id, amount = limit)
            except Exception as error:
                print(f"Request failed while trying user_following({user_name}, {limit}):\n{error}\n\n")
                sys.exit("No profiles could be fetched. Tried three different methods. Exiting...")
        except Exception as exc:
            print(f"Request failed while trying user_following_gql({user_name}, {limit}):\n{exc}\n\n")
    except Exception as e:
        print(f"Failed to get profiles {user_name}'s following:\n{e}\n\n")
        sys.exit("No profiles fetched using three different methods. Exiting...")
    return res

def followers(client, user_name, limit: int = 100):
    fws = {}
    user_id = client.user_id_from_username(user_name)
    try:
        print(f"Trying using user_followers_v1({user_id}, {limit})...\n")
        fws = client.user_followers_v1(user_id, amount = limit)
    except (ClientBadRequestError, requests.HTTPError) as exception:
        try:
            print(f"Bad request while getting {user_name}:\n{exception}\n\n")
            print(f"Trying via user_followers_gql({user_name}, {limit}) method...\n")
            fws = client.user_followers_gql(user_id, amount = limit)
        except (RetryError, Exception) as retry_error:
            print(f"Retry error while getting requesting via user_followers_gql() {user_name}:\n{retry_error}\n\n")
            try:
                print(f"Trying again using user_followers({user_id}, {limit}) method...\n")
                fws = client.user_followers(user_id, amount = limit)
            except Exception as error:
                print(f"Request failed while trying user_followers({user_name}, {limit}):\n{error}\n\n")
                sys.exit("No followers could be fetched. Tried three different methods. Exiting...")
        except Exception as exc:
            print(f"Request failed while trying user_followers_gql({user_name}, {limit}):\n{exc}\n\n")
            # sys.exit("No followers fetched. Exiting...")
    except Exception as e:
        print(f"Failed to get {user_name}'s followers:\n{e}\n\n")
        sys.exit("No followers fetched using three different methods. Exiting...")
    return fws

def write_followers_to_file(sorted_users_dict):
    print(f"\nSaving {len(sorted_users_dict)} usernames to the to_follow.log file in the current directory.\n")
    cnt = 0
    for users_row in sorted_users_dict:
        with open("to_follow.log", "a") as log_usernames:
            log_usernames.write(f"{users_row['un']}\n")
        cnt += 1
    print(f"Total number of saved profiles: {cnt}. For more information, see “to_follow.log file.”\n")

def follow_users_from_file(cl, file_name: str):
    with open(file_name) as my_file:
        print(f"Reading your file: {file_name}...")
        f = my_file.read().split("\n")
        i = 0
        for row in f:
            if bool(row):
                try:
                    row = str(row.strip())
                    user_id = cl.user_id_from_username(row)
                    cl.user_follow(user_id)
                    i += 1
                    print(f"Followed user: {row}")
                    print(f"Total profiles followed so far: {i}")
                    with open("success.log", "a") as log:
                        log.write(f"Followed user: {row}\n")
                except Exception as e:
                    print(f"Failed to follow {row}:\n{e}\n\n")
                    with open("errors.log", "a") as log:
                        log.write(f"{row}: {e}\n")
                    continue

def login_user(client: Client):
    """
    Attempts to log in to Instagram using either the provided session information
    or the provided username and password.
    """

    session = client.load_settings("session.json")

    login_via_session = False
    login_via_pw = False

    if session:
        try:
            client.set_settings(session)
            client.login(USERNAME, PASSWORD)

            # check if session is valid
            try:
                client.get_timeline_feed()
            except LoginRequired:
                logger.info("Session is invalid, need to login via username and password")

                old_session = client.get_settings()

                # use the same device uuids across logins
                client.set_settings({})
                client.set_uuids(old_session["uuids"])

                client.login(USERNAME, PASSWORD)
            login_via_session = True
        except Exception as e:
            logger.info("Couldn't login user using session information: %s" % e)

    if not login_via_session:
        try:
            logger.info("Attempting to login via username and password. username: %s" % USERNAME)
            if client.login(USERNAME, PASSWORD):
                login_via_pw = True
        except Exception as e:
            logger.info("Couldn't login user using username and password: %s" % e)

    if not login_via_pw and not login_via_session:
        raise Exception("Couldn't login user with either password or session\n")
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientBadRequestError
import logging, requests
from dotenv import dotenv_values

config = dotenv_values(".env")

USERNAME = config['USERNAME']
PASSWORD = config['PASSWORD']

logger = logging.getLogger()

def followers(client, user_name, limit: int = 100):
    fws = {}
    user_id = client.user_id_from_username(user_name)
    try:
        print(f"Trying using user_followers_v1({user_id}, {limit})...\n")
        fws = client.user_followers_v1(user_id, amount = limit)
    except (ClientBadRequestError, requests.HTTPError) as exception:
        try:
            print(f"Bad request while getting {user_name}:\n{exception}\n\n")
            print(f"Trying via user_followers_gql({user_name}, {limit})...\n")
            fws = client.user_followers_gql(user_id, amount = limit)
        except Exception as exc:
            print(f"Request failed while trying user_followers_gql({user_name}, {limit}):\n{exc}\n\n")
            try:
                print(f"Trying again using user_followers({user_id}, {limit})...\n")
                fws = client.user_followers(user_id, amount = limit)
            except Exception as error:
                print(f"Request failed while trying user_followers({user_name}, {limit}):\n{error}\n\n")
    except Exception as e:
        print(f"Failed to get {user_name}'s followers using three different methods:\n{e}\n\n")
    return fws

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
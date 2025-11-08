from instagrapi import Client
import _helpers as h
import sys

# adds a random delay between x and y seconds after each request (otherwise your account can be blocked)
x = 1
y = 3
# collect data of the first 'limit_followers_count' followers (more data = more time is needed to collect it)
limit_followers_count = 500
# consider only users with this number of followers or more
add_users_with_num_of_followers = 800

# establish the connection & login
cl = Client()
cl.delay_range = [x, y]
h.login_user(cl)
cl.dump_settings("session.json")

# https://subzeroid.github.io/instagrapi/usage-guide/best-practices.html
# before_ip = cl._send_public_request("https://api.ipify.org/")
# cl.set_proxy("http://<api_key>:wifi;ca;;;toronto@proxy.soax.com:9137")
# after_ip = cl._send_public_request("https://api.ipify.org/")
#
# print(f"Before: {before_ip}")
# print(f"After: {after_ip}")

username = input("Enter the username to analyze: ")
print(f"You've entered '{username}', getting the user data...\n")

result = h.followers(cl, username, limit_followers_count)
followers_count = len(result)
if followers_count <= 0:
    sys.exit("No followers found. Exiting...")

print(f"Collecting data for {followers_count} followers of '{username}'.\nThis may last between {followers_count * x * 2} and {followers_count * y * 2} seconds or {(followers_count * x * 2 / 60):.2f} and {(followers_count * y * 2 / 60):.2f} minutes...\n")

users = []
for res in result:
    res = dict(res)
    user_info = dict(cl.user_info_by_username(res["username"]))
    if user_info["follower_count"] > add_users_with_num_of_followers:
        users.append({'id': res["pk"], 'un': res["username"], 'fw': user_info["follower_count"]})

sorted_users = sorted(users, key = lambda x:x['fw'], reverse = True)

print(f"Collected {len(sorted_users)} big followers of '{username}'.\n")

limit_top = 10
limit = len(sorted_users) if (len(sorted_users) < limit_top * 2) else limit_top
print(f"\nListing the TOP {limit} big followers of '{username}':\n")
print('ID\t\t\tUsername\t\t\tNumber of followers\n')
index = 0
for user in sorted_users:
    print('{}\t\t{}\t\t\t{}'.format(user['id'], user['un'], user['fw']))
    index += 1
    if index == limit:
        break

"""
#0 list(41) 
    [0] => dict(3) 
        ['id'] => str(9) "456891722"
        ['un'] => str(10) "albana.bee"
        ['fw'] => int(21172) 
    [1] => dict(3) 
        ['id'] => str(10) "8484023319"
        ['un'] => str(15) "richardeisenach"
        ['fw'] => int(20428) 
    [2] => dict(3) 
        ['id'] => str(10) "9250205401"
        ['un'] => str(22) "stadtstrandduesseldorf"
        ['fw'] => int(17623)
"""

user_input = input(f"\nDo you want to auto follow these {len(sorted_users)} users with this account? (yes/no): ")
if user_input.lower() in ["yes", "y"]:
    print("Continuing...")
    for users_row in sorted_users:
        try:
            print(f"Start following user: {users_row['un']}...")
            cl.user_follow(users_row['id'])
            print(f"Followed user: {users_row['un']} ({users_row['fw']} followers).")
            with open("success.log", "a") as log:
                log.write(f"Followed user: {users_row['un']} ({users_row['fw']} followers)\n")
        except Exception as exc:
            print(f"Failed to follow {users_row['un']}: {exc}")
            with open("errors.log", "a") as log_err:
                log_err.write(f"{users_row['un']}: {exc}\n")
        continue
else:
    print(f"\nStopping...\nSaving {len(sorted_users)} usernames to the to_follow.log file in the current directory.\n")
    for users_row in sorted_users:
        with open("to_follow.log", "a") as log_usernames:
            log_usernames.write(f"{users_row['un']}\n")
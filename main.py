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

limit_top = 15
limit = len(sorted_users) if (len(sorted_users) < limit_top * 2) else limit_top
print(f"\nListing the TOP {limit} big followers of '{username}':\n")
print('ID\t\t\tUsername\t\t\tNumber of followers\n')
index = 0
for user in sorted_users:
    print('{}\t\t{}\t\t\t{}'.format(user['id'], user['un'], user['fw']))
    index += 1
    if index == limit:
        break

print(f"\nOverall {len(sorted_users)} big followers with ≥{add_users_with_num_of_followers} each of '{username}' were found.\n")
user_input = input(f"\nDo you want to auto follow these users with this account (you can specify how many in the next step)? (yes/no): ")
if user_input.lower() in ["yes", "y"]:
    num_of_profiles_to_follow = input(
        f"\nHow many profiles out of {len(sorted_users)} do you want to follow (please enter a valid number)? Normally, Instagram accepts up to 30 follow operations/session: ")
    max_val = int(num_of_profiles_to_follow.strip())
    if not isinstance(max_val, int):
        print(f"\nYour input was incorrect... Saving profiles into a file...\n")
        h.write_followers_to_file(sorted_users)
    print(f"Your input was to follow {max_val} profiles. Starting the auto-following process...\n")
    count = 0
    for users_row in sorted_users:
        try:
            print(f"Start following user: {users_row['un']}...")
            cl.user_follow(users_row['id'])
            print(f"Followed user: {users_row['un']} ({users_row['fw']} followers).")
            with open("success.log", "a") as log:
                log.write(f"Followed user: {users_row['un']} ({users_row['fw']} followers)\n")
            count += 1
            print(f"Total number of big profiles followed up to now: {count} out of {max_val}.")
            if count >= max_val:
                break
        except Exception as exc:
            print(f"Failed to follow {users_row['un']}: {exc}")
            with open("errors.log", "a") as log_err:
                log_err.write(f"{users_row['un']}: {exc}\n")
        continue
else:
    h.write_followers_to_file(sorted_users)
# This script collects the public data of a user on Instagram. After that you have a choice between three modes:
    [1] auto-follow users read from a given file (the profiles should be separated by line: "\n"),
    [2] collect the data of user's followers & auto-follow the top ones (optional),
    [3] collect the data of profiles user is following & auto-follow the major ones (optional).

My script is based on [instagrapi](https://github.com/subzeroid/instagrapi) library.

### 1) This script reads a text file line by line with some delay. The list should be a plain text file (without any headers) with usernames on each line in order for the script to work auto-follow them.
__Warning__: there's no limit of requests sent to Instagram in this mode: each line in the file will produce 2 requests.
For instance, if the file contains 30 usernames, 60 requests will be made.
Instagram may block your IP for 24-72 hours. It's recommended to use [proxies](https://subzeroid.github.io/instagrapi/usage-guide/best-practices.html).

### 2) The major followers of a user will be collected, sorted, displayed and either auto-followed or saved to a file.

### 3) The major profiles a user is following will be collected, sorted, displayed and either auto-followed ([instagrapi](https://github.com/subzeroid/instagrapi) is being used) or saved to a file.

### The script also does the sorting of the collected user profiles by the number of followers of each user profile:

    1. it gets the user info of each profile of an analysed user
    2. it gets the number of followers of each profiles that's being analysed
    3. it sorts by the number of followers from (2) and outputs the top 10-20 followers (depending on the 'limit_top' variable).

If you need to collect the usernames first, use the following Chrome Extensions: [igfollow-follower-export](https://chromewebstore.google.com/detail/igfollow-follower-export) or 
[instagram-follower-collector](https://phantombuster.com/automations/instagram/7175/instagram-follower-collector) or alike.

## How to start:
### Prerequisites: https://github.com/subzeroid/instagrapi
`pip install instagrapi`

Read their [docs](https://subzeroid.github.io/instagrapi/usage-guide/user.html).
### Optional:
`pip install python-dotenv`

See & change USERNAME & PASSWORD at the top of [_helpers.py](_helpers.py).

### Change the values of the following variables in [main.py](main.py) according to your needs:
 - __limit_followers_count__ – how many followers to read/collect/analyse,
 - __limit_following_count__ – how many profiles the user you've entered is following to read/collect/analyse,
 - __add_users_with_num_of_followers__ – only collect & auto-follow user profiles with that value, and 
 - __limit_top__ – limit the list of top users to this value.

## Known issues
#### - After some time of using the script, especially the auto follow function, you might get a message:
"feedback_required: We limit how often you can do certain things on Instagram, like following people, to protect our community. Let us know if you think we made a mistake."

In that case you'll have to wait for up to 24 hours to be able to follow users again.

#### - Some _update_headers_ error messages can appear while using 'extract_user_gql()' or 'user_info_by_username_gql()' functions.
Please look into this issue first if that's your case: https://github.com/subzeroid/instagrapi/issues/2266

I had to move _update_headers_ parameter in the user_info_by_username_gql() function in user.py to make it work:

![user_info_by_username_gql.jpg](user_info_by_username_gql.jpg)

Apparently this issue still hasn't been fixed throughout the whole codebase in the [2.2.1](https://github.com/subzeroid/instagrapi/releases/tag/2.2.1) release of [instagrapi](https://github.com/subzeroid/instagrapi).
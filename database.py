from pysondb import db as database

db = database.getDb("db.json")


def get_user(id):

    try:
        print("[!] Trying to get user")
        user = db.getByQuery({"user_id": id})[0]
        print("[+] Got user")

    except:
        print("[!] User not found")
        user = None

    return user


def create_user(id):

    if get_user(id) is None:

        print("[+] Creating user " + str(id))
    
        db.add({"user_id": id, "active_titles":[], "cat_active_title": ""})


def adding_active_title(id, id_titles):

    active_user = get_user(id)

    if active_user:

        print("[+] Adding active title " + str(id_titles) + " to user " + str(id))

        active_user["cat_active_title"] = id_titles
    
    db.updateByQuery({"user_id": id}, active_user)


def create_user_title(id, title):
    active_user = get_user(id)

    if active_user:

        print("[+] Adding title " + str(title) + " to user " + str(id))

        if title not in active_user["active_titles"]:
            active_user["active_titles"].append(title)
    
    
    db.updateByQuery({"user_id": id}, active_user)


def delete_user_title(id, title_id):
    active_user = get_user(id)

    if active_user:

        print("[+] Removing title with ID: " + str(title_id) + " from user " + str(id))

        active_user["active_titles"].pop(title_id)
    
    db.updateByQuery({"user_id": id}, active_user)


def get_users_by_title(title):

    users = db.getAll()

    result_users = []

    for user in users:

        if title in user["active_titles"]:
            result_users.append(user)

    return result_users
def calculate_total(items, discount):
    return sum(items) * (1 - discount)


def get_user(user_id, db):
    return db.query(user_id)

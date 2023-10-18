

def sql_execute(query, *args, **kwargs):
    print(*args)


sql_execute("SELECT * FROM users WHERE id = ?", 1, 2, 3)
class UserRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def get_by_username(self, username):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
            user = cursor.fetchone()
        return user


    def get_role_id_by_user_id(self, user_id):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT role_id FROM users WHERE id = %s;", (user_id,))
            role_id = cursor.fetchone()
        return role_id
    
    def get_is_admin_by_id(self, user_id):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            # Сначала получаем role_id пользователя
            cursor.execute("""
                SELECT role_id
                FROM users
                WHERE id = %s
            """, (user_id,))
            user = cursor.fetchone()

            if user:
                role_id = user.role_id

                # Теперь проверяем, что роль с этим ID называется 'admin'
                cursor.execute("""
                    SELECT name
                    FROM roles
                    WHERE id = %s
                """, (role_id,))
                role = cursor.fetchone()

                if role and role.name == 'admin':
                    return True
            return False

    def get_by_id(self, user_id):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
            user = cursor.fetchone()
        return user
    
    def get_by_username_and_password(self, username, password):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s AND password_hash = SHA2(%s, 256);", (username, password))
            user = cursor.fetchone()
        return user
    
    def all(self):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("SELECT users.*, roles.name AS role FROM users LEFT JOIN roles ON users.role_id = roles.id")
            user = cursor.fetchall()
        return user
    
    def create(self, username, password, first_name, middle_name, last_name, role_id):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple=True) as cursor:
            query = (
                "INSERT INTO users (username, password_hash, first_name, middle_name, last_name, role_id) VALUES"
                "(%s, SHA2(%s, 256), %s, %s, %s, %s)" 
            )
            user_data = (username, password, first_name, middle_name, last_name, role_id)
            cursor.execute(query, user_data)
            connection.commit()

    def update(self, user_id, first_name, middle_name, last_name, role_id):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple=True) as cursor:
            query = (
                "UPDATE users SET first_name = %s,"
                "middle_name = %s, last_name = %s, "
                "role_id = %s WHERE id = %s"
            )
            user_data = (first_name, middle_name, last_name, role_id, user_id)
            cursor.execute(query, user_data)
            connection.commit()

    def delete(self, user_id):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple=True) as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            connection.commit()
    
    def update_password(self, user_id, new_password):
        connection = self.db_connector.connect()
        with connection.cursor(named_tuple=True) as cursor:
            cursor.execute(
                "UPDATE users SET password_hash = SHA2(%s, 256) WHERE id = %s",
                (new_password, user_id)
            )
            connection.commit()


    def has_role(self, user_id, role_name):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("""
                SELECT r.name
                FROM users u
                JOIN roles r ON u.role_id = r.id
                WHERE u.id = %s
            """, (user_id,))
            row = cursor.fetchone()
            return row and row.name == role_name


    def get_role_name(self, user_id):
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute("""
                SELECT r.name
                FROM users u
                JOIN roles r ON u.role_id = r.id
                WHERE u.id = %s
            """, (user_id,))
            row = cursor.fetchone()
            return row.name if row else None

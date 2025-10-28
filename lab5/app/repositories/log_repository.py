class LogRepository:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def get_all_with_users(self, user_id=None, is_admin=False, limit=20, offset=0):
        query = """
            SELECT 
                v.id,
                v.path,
                v.created_at,
                CONCAT(u.last_name, ' ', u.first_name, ' ', IFNULL(u.middle_name, '')) AS user_name
            FROM visit_logs v
            LEFT JOIN users u ON v.user_id = u.id
        """

        params = []
        if not is_admin:
            query += " WHERE v.user_id = %s"
            params.append(user_id)

        query += " ORDER BY v.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
        
    def count_all(self, user_id=None, is_admin=False):
        query = "SELECT COUNT(*) as total FROM visit_logs"
        params = []

        if not is_admin:
            query += " WHERE user_id = %s"
            params.append(user_id)

        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone().total

    def get_by_page(self, user_id=None, is_admin = False):
        query = """
        SELECT path, COUNT(*) AS visits
                FROM visit_logs
                GROUP BY path
                ORDER BY visits DESC
        """

        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute(query)
            logs = cursor.fetchall()
        return logs
    
    def get_by_users(self):
        query = """
        SELECT u.first_name, u.last_name, COUNT(v.id) AS visits
        FROM visit_logs v
        LEFT JOIN users u ON v.user_id = u.id
        GROUP BY u.id
        ORDER BY visits DESC
        """
        with self.db_connector.connect().cursor(named_tuple=True) as cursor:
            cursor.execute(query)
            logs = cursor.fetchall()
        return logs

import sqlite3
import json
from global_config import DATABASE


class ConfigMGR:

    def __init__(self):
        pass  # No action is needed in constructor for now

    def get_conf(self, username):
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT * FROM users WHERE username = ?
                ''', (username, ))
            user_row = cursor.fetchone()
            if user_row:
                # Convert the row to a dictionary
                columns = [desc[0] for desc in cursor.description]
                user_db = [dict(zip(columns, user_row))][0]
                user_id = user_db['id']

                courses = self.get_courses(user_id, cursor)
                courses_list = [
                    dict(
                        zip([
                            'course_id', 'course_name', 'type', 'maxshow',
                            'order', 'msg'
                        ], course)) for course in courses
                ]

                checks = self.get_checks(user_id, cursor)
                checks_list = [
                    dict(zip(['name', 'type'], check)) for check in checks
                ]

                user_conf = {
                    "username": user_db['username'],
                    "semester_begin": user_db['semester_begin'],
                    "url": user_db['url'],
                    "bid": user_db['bid'],
                    "timeformat": user_db['timeformat'],
                    "background_image": user_db['background_image'],
                    "courses": courses_list,
                    "checks": checks_list
                }
                return user_conf
            else:
                return {"version": 1}

    def write_conf(self, username, configuration):
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()

            # Update the user's data in the 'users' table
            user_fields = ', '.join(
                f'{key} = ?' for key in configuration
                if key not in ['id', 'username', 'checks', 'courses'])
            user_values = [
                value for key, value in configuration.items()
                if key not in ['id', 'username', 'checks', 'courses']
            ]
            user_values.append(username)
            cursor.execute(
                f'''
                UPDATE users SET {user_fields} WHERE username = ?
            ''', user_values)

            # Get the user_id for the given username
            cursor.execute("SELECT id FROM users WHERE username = ?",
                        (username, ))
            user_id = cursor.fetchone()[0]

            # Upsert checks data
            if 'checks' in configuration:
                for check in configuration['checks']:
                    check_fields = ', '.join(check.keys())
                    check_placeholders = ', '.join(['?'] * len(check))
                    check_values = list(check.values())
                    cursor.execute(
                        f'''
                        INSERT OR REPLACE INTO checks ({check_fields}, user_id) VALUES ({check_placeholders}, ?)
                    ''', (*check_values, user_id))

            # Upsert courses data
            if 'courses' in configuration:
                for course in configuration['courses']:
                    course_fields = ', '.join(course.keys()).replace('order', 'display_order')
                    course_placeholders = ', '.join(['?'] * len(course))
                    course_values = list(course.values())
                    cursor.execute(
                        f'''
                        INSERT OR REPLACE INTO courses ({course_fields}, user_id) VALUES ({course_placeholders}, ?)
                    ''', (*course_values, user_id))

            conn.commit()

    def remove_key(self, username, key):
        configuration = self.get_conf(username)
        if key in configuration:
            configuration[key] = None  # Set to None to remove
            self.write_conf(username, configuration)

    def set_key_value(self, username, key, value):
        configuration = self.get_conf(username)
        configuration[key] = value
        self.write_conf(username, configuration)

    def set_wallpaper_path(self, username, path):
        self.set_key_value(username, "wallpaper_path", path)

    def get_checks(self, user_id, cursor):
        cursor.execute(
            '''
            SELECT name, type FROM checks WHERE user_id = ?
            ''', (user_id, ))
        return cursor.fetchall()

    def get_courses(self, user_id, cursor):
        cursor.execute(
            '''
            SELECT course_id, course_name, type, maxshow, display_order, msg FROM courses WHERE user_id = ?
            ''', (user_id, ))
        return cursor.fetchall()

    def get_user_cache(self, user_id, cursor):
        cursor.execute(
            '''
            SELECT * FROM user_cache WHERE user_id = ?
            ''', (user_id, ))
        return cursor.fetchone()

import MySQLdb
from MySQLdb.connections import OperationalError


class DB:

    def __init__(self, db='root', host='localhost', user='root', passwd=''):
        self.db = db
        self.host = host
        self.user = user
        self.passwd = passwd
        self.conn = None

    def connect(self):
        self.conn = MySQLdb.connect(user=self.user, host=self.host,
                                    passwd=self.passwd, db=self.db)
        return self

    def cursor(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("select * from document limit 1")
        except Exception: # No se capturan las otras
            self.connect()
            cursor = self.conn.cursor()
        return cursor



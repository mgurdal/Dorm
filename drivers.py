class BaseDriver(object):
    def __init__(self, conn):
        super(BaseDriver, self).__init__()
        self.conn = conn
        self.__tables__ = {}

class Sqlite(BaseDriver):
    def __init__(self, conf):
        self.conn = sqlite3.connect(database=self.database,
                                    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
                                    )
        self.conf = conf
        super(Sqlite, self).__init__(conn=self.conn)
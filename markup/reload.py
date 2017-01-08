import sqlite3
import os.path


if __name__ == '__main__':
        database = 'database'
        if os.path.exists(database) and os.path.isfile(database):
            os.remove(database)
        connection = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()
        cursor.execute('create table Descriptions(Picture text, Description text)')
        cursor.execute('CREATE TABLE Comments(Picture TEXT, Comment TEXT, Time timestamp, Ip TEXT)')
        cursor.execute('create table LastVisitUsers(Ip text, Time timestamp)')
        cursor.execute('create table Likes(Picture text, Ip text)')
        connection.commit()
        cursor.close()
        connection.close()

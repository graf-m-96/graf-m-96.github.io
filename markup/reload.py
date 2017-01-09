import sqlite3
import os.path


if __name__ == '__main__':
        database = 'database'
        if os.path.exists(database) and os.path.isfile(database):
            os.remove(database)
        connection = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()
        cursor.execute('CREATE table Pictures(Picture text)')

        cursor.execute('''insert into Pictures values
                      ('emily.jpg'), ('lichess.jpg'), ('music.jpg'), ('people_vs_kuka.jpg'), ('стартовая.png'),
                      ('ферма.png'), ('among_beginners_1.jpg'), ('among_beginners_2.jpg'), ('among_beginners_3.jpg'),
                      ('among_beginners_4.jpg'), ('among_beginners_5.jpg'), ('among_beginners_6.jpg'),
                      ('quarterfinal_1.jpg'), ('quarterfinal_2.jpg'), ('quarterfinal_3.jpg'), ('quarterfinal_4.jpg'),
                      ('selection_on_quarterfinal_1.jpg'), ('selection_on_quarterfinal_2.jpg'),
                      ('selection_on_quarterfinal_3.jpg'), ('selection_on_quarterfinal_4.jpg'),
                      ('selection_on_quarterfinal_5.jpg'), ('selection_on_quarterfinal_6.jpg'),
                      ('selection_on_quarterfinal_7.jpg')''')

        cursor.execute('CREATE TABLE Comments(Picture TEXT, Comment TEXT, Time timestamp, Ip TEXT)')
        cursor.execute('create table LastVisitUsers(Ip text, Time timestamp)')
        cursor.execute('create table Likes(Picture text, Ip text)')
        connection.commit()
        cursor.close()
        connection.close()

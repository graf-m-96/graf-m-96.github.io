import tornado.web
import tornado.gen
import tornado.ioloop
import datetime
import sqlite3
import signal
import os
import re
import traceback
import threading
import xlwt
import io


def check():
    global STOP
    if STOP:
        tornado.ioloop.IOLoop.instance().stop()
        if CONNECTION_WITH_DB:
            CONNECTION_WITH_DB.close()


class HandlerMain(tornado.web.RequestHandler):
    def get(self):
        try:
            cursor = CONNECTION_WITH_DB.cursor()
            visit = datetime.datetime.now()
            ip = self.request.remote_ip
            cursor.execute('select Time from LastVisitUsers where Ip=?', (ip,))
            last_visit = cursor.fetchone()
            if not last_visit or (visit - last_visit[0]).seconds > TIMEOUT_BETWEEN_VISITS:
                with LOCK_TABLE_VISITS:
                    global QUANTITY_VISITORS
                    QUANTITY_VISITORS += 1
                    if last_visit:
                        cursor.execute('update LastVisitUsers set Time=? where Ip=?', (visit, ip))
                    else:
                        cursor.execute('insert into LastVisitUsers values (?,?)', (ip, visit))
                    CONNECTION_WITH_DB.commit()
        except Exception:
            traceback.print_exc()
        finally:
            cursor.close()
            self.render('index.html', number=QUANTITY_VISITORS)


class HandlerСommentsRequest(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        try:
            picture = self.get_argument('name')
            self.set_header('Cache-Control', 'no-cache')
            cursor = CONNECTION_WITH_DB.cursor()
            self.write(self.description_picture(cursor, picture))
            self.flush()
            cursor.execute('select Comment from Comments where Picture=? order by Time', (picture,))
            for comment in cursor:
                self.write(comment[0])
                yield tornado.gen.Task(self.flush)
            self.write('</div>')
            self.flush()
        except Exception as error:
            traceback.print_exc()
            if isinstance(error, tornado.web.HTTPError):
                raise tornado.web.HTTPError(404)
            else:
                raise tornado.web.HTTPError(500)
        finally:
            self.finish()
            try:
                cursor.close()
            except NameError:
                pass

    def description_picture(self, cursor, picture):
        cursor.execute('select Description from Descriptions where Picture=?', (picture,))
        description = cursor.fetchone()
        if isinstance(description, tuple):
            return description[0]
        else:
            raise tornado.web.HTTPError(404)


class HandlerAddComment(tornado.web.RequestHandler):
    def post(self):
        try:
            picture = self.get_argument('picture')
            comment = self.get_comment()
            cursor = CONNECTION_WITH_DB.cursor()
            time_request = datetime.datetime.now()
            ip = self.request.remote_ip
            if self.opportunity_to_comment(cursor, picture, comment, time_request):
                with LOCK_TABLE_COMMENTS:
                    cursor.execute('insert into Comments values (?,?,?,?)', (picture, comment, time_request, ip))
                    CONNECTION_WITH_DB.commit()
        except Exception:
            traceback.print_exc()
        finally:
            self.finish()
            try:
                cursor.close()
            except NameError:
                pass

    def get_comment(self):
        max_len_comment = 500
        comment = re.sub("&#", "", self.get_argument('comment')[:max_len_comment])
        if len(comment) == 0:
            raise Exception
        comment = re.sub("<", "&lt;", re.sub(">", "&gt;", comment))
        comment = re.sub(r'&lt;(img src="https?://[a-zA-Zа-яА-Я0-9\.~`!@#\$;%\^:&\?\*\(\)/\\_\-\+=]+")&gt;',
                           r'<\1 class="imgInComment" alt="image">', comment, flags=re.IGNORECASE)
        comment = re.sub(r'&lt;b&gt;(.+)&lt;/b&gt;', r'<b>\1</b>', comment, flags=re.IGNORECASE)
        comment = re.sub(r'&lt;i&gt;(.+)&lt;/i&gt;', r'<i>\1</i>', comment, flags=re.IGNORECASE)
        return "<p>"+comment+"<hr></p>"

    def opportunity_to_comment(self, cursor, picture, comment, time_request):
        ip = self.request.remote_ip
        cursor.execute('select Time from Comments where Ip=? order by Time desc limit ?', (ip, MAXIMUM_NUMBER_COMMENTS))
        time_last_comments = cursor.fetchall()
        if time_last_comments:
            cursor.execute('select Picture, Comment from Comments where Ip=? and Time=(select max(Time) from Comments where Ip=?)', (ip, ip))
            last_picture, last_comment = cursor.fetchone()
            if len(time_last_comments) < MAXIMUM_NUMBER_COMMENTS and (picture != last_picture or comment != last_comment):
                return True
            if (time_request - min(time_last_comments)[0]).seconds > TIME_LOCK and (picture != last_picture or comment != last_comment):
                return True
            return False
        return True


class HandlerLikesRequest(tornado.web.RequestHandler):
    def get(self):
        try:
            self.set_header('Cache-Control', 'no-cache')
            self.set_header('Access-Control-Allow-Origin', '*')
            picture = self.get_argument('name')
            cursor = CONNECTION_WITH_DB.cursor()
            cursor.execute('select count(*) from Likes where Picture=?', (picture,))
            likes = cursor.fetchone()[0]
            self.write('<p style="display: inline; font-weight: 100">{}</p>'.format(likes))
            self.flush()
        except Exception:
            traceback.print_exc()
        finally:
            self.finish()


class HandlerAddLike(tornado.web.RequestHandler):
    def get(self):
        try:
            picture = self.get_argument('name')
            cursor = CONNECTION_WITH_DB.cursor()
            ip = self.request.remote_ip
            cursor.execute('select * from Likes where Picture=? and Ip=?', (picture, ip))
            like_was = cursor.fetchone()
            with LOCK_TABLE_LIKES:
                if like_was:
                    cursor.execute('delete from Likes where Picture=? and Ip=?', (picture, ip))
                else:
                    cursor.execute('insert into Likes values (?, ?)', (picture, ip))
                CONNECTION_WITH_DB.commit()
        except Exception:
            traceback.print_exc()
        finally:
            cursor.close()
            self.finish()


# class HandlerDownloadXLS(tornado.web.RequestHandler):
# 	@tornado.web.asynchronous
# 	@tornado.gen.engine
# 	def get(self):
# 		try:
# 			self.set_header('Content-Type', 'application/excel')
# 			self.set_header('Content-Disposition', 'attachment; filename="galeryDetails.xls"')
# 			xls = self.xls()
# 			chunk = 512000
# 			data = xls.read(chunk)
# 			while data:
# 				self.write(data)
# 				yield tornado.gen.Task(self.flush)
# 				data = xls.read(chunk)
# 			self.flush()
# 		except Exception:
# 			traceback.print_exc()
# 		finally:
# 			self.finish()


# 	def xls(self):
# 		try:
# 			cursor = CONNECTION_WITH_DB.cursor()
# 			book = xlwt.Workbook()
# 			table = book.add_sheet('Photo details')
# 			table.write(0, 0, 'Photo')
# 			table.write(0, 1, 'Quantity comments')
# 			table.write(0, 2, 'Quantity likes')
# 			cursor.execute('select distinct Picture from Descriptions')
# 			pictures = list(map(lambda item: item[0], cursor.fetchall()))
# 			for row, picture in enumerate(pictures, 1):
# 				table.write(row, 0, picture)
# 				cursor.execute('select count(Comment) from Comments where Picture=?', (picture,))
# 				comments = cursor.fetchone()[0]
# 				cursor.execute('select count(Ip) from Likes where Picture=?', (picture,))
# 				likes = cursor.fetchone()[0]
# 				table.write(row, 1, comments)
# 				table.write(row, 2, likes)
# 			buff = io.BytesIO()
# 			book.save(buff)
# 			buff.seek(0)
# 			return buff
# 		except Exception:
# 			traceback.print_exc()
# 		finally:
# 			cursor.close()


def quantity_visitors():
    cursor = CONNECTION_WITH_DB.cursor()
    cursor.execute('select count(*) from LastVisitUsers')
    quantity = cursor.fetchone()
    cursor.close()
    return quantity[0] if isinstance(quantity, tuple) else 0


STOP = False
HANDLERS = [(r'/', HandlerMain),
            (r'/(common\.css)', tornado.web.StaticFileHandler, {'path': ''}),
            (r'/(index\.css)', tornado.web.StaticFileHandler, {'path': ''}),
            (r'/pictures/(.+)', tornado.web.StaticFileHandler, {'path': 'pictures'}),
            (r'/(gallery\.html)', tornado.web.StaticFileHandler, {'path': ''}),
            (r'/(gallery\.css)', tornado.web.StaticFileHandler, {'path': ''}),
            (r'/(gallery\.js)', tornado.web.StaticFileHandler, {'path': ''}),
            (r'/(links\.html)', tornado.web.StaticFileHandler, {'path': ''}),
            (r'/(links\.css)', tornado.web.StaticFileHandler, {'path': ''}),
            # (r'/(.+)', tornado.web.StaticFileHandler, {'path': ''}),
            (r'/getComments', HandlerСommentsRequest),
            (r'/addComment', HandlerAddComment),
            (r'/getLikes', HandlerLikesRequest),
            (r'/addLike', HandlerAddLike)
            # ,(r'/downloadXLS', HandlerDownloadXLS)
            ]


CONNECTION_WITH_DB = None
MAXIMUM_NUMBER_COMMENTS = 10
TIME_LOCK = 3600
TIMEOUT_BETWEEN_VISITS = 1800
QUANTITY_VISITORS = 0
LOCK_TABLE_COMMENTS = threading.Lock()
LOCK_TABLE_VISITS = threading.Lock()
LOCK_TABLE_LIKES = threading.Lock()

if __name__ == '__main__':
    CONNECTION_WITH_DB = sqlite3.connect('database', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    QUANTITY_VISITORS = quantity_visitors()
    application = tornado.web.Application(handlers=HANDLERS)
    # application.listen(address="0.0.0.0", port=80)
    application.listen(address='localhost', port=8080)
    tornado.ioloop.PeriodicCallback(check, 1000).start()
    tornado.ioloop.IOLoop.instance().start()

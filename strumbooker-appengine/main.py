#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
from google.appengine.ext.db import Key
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template

class Book(db.Model):
	userid = db.StringProperty()
	name = db.StringProperty()
	sheetCounter = db.IntegerProperty()
	
class Sheet(db.Model):
	"""Models an individual Sheet"""
	author = db.UserProperty()
	song = db.StringProperty()
	artist = db.StringProperty()
	content = db.StringProperty(multiline=True)
	createDate = db.DateTimeProperty(auto_now_add=True)
	shared = db.BooleanProperty()
	
class BookHandler(webapp2.RequestHandler):
	
	def get(self):
		
		user = users.get_current_user()
		
		if user is None:
			self.redirect(users.create_login_url(self.request.uri))
			return
		
		path = os.path.join(os.path.dirname(__file__), 'new_book.html')
		self.response.out.write(template.render(path, {}))
		
	def post(self):
		
		user = users.get_current_user()
		
		if user is None:
			self.redirect(users.create_login_url(self.request.uri))
			return
		
		book = Book()
		book.name = self.request.get('name')
		book.userid = user.user_id()
		book.sheetCounter = 0
		book.put()
		
		self.redirect('/books.html');
		
class BooksHandler(webapp2.RequestHandler):
	
	def get(self):
		
		user = users.get_current_user()
		
		if user is None:
			self.redirect(users.create_login_url(self.request.uri))
			return
		
		books = db.GqlQuery("SELECT * FROM Book WHERE userid = :1", user.user_id())
		
		template_params = {
			'books': books,
		}
		
		path = os.path.join(os.path.dirname(__file__), 'books.html')
		self.response.out.write(template.render(path, template_params))
		
class NewSheetHandler(webapp2.RequestHandler):
	
	def get(self):

		user = users.get_current_user()
		
		if user is None:
			self.redirect(users.create_login_url(self.request.uri))
			return
		
		bookKey = Key(self.request.get('book'))
		q = db.GqlQuery("SELECT * FROM Book WHERE __key__ = :1", bookKey)
		book = q.get()
		
		if book is None or book.userid != user.user_id():
			self.redirect('/books.html');
			return
		else:
			template_values = {
				'book': book
	        }
	
			path = os.path.join(os.path.dirname(__file__), 'new_sheet.html')
			self.response.out.write(template.render(path, template_values))		
	
	def post(self):
		
		user = users.get_current_user()
		
		if user is None:
			self.redirect(users.create_login_url(self.request.uri))
			return
		
		bookKey = Key(self.request.get('book'))
		q = db.GqlQuery("SELECT * FROM Book WHERE __key__ = :1", bookKey)
		book = q.get()
		
		sheet = Sheet(parent=book)
		sheet.author = user
		sheet.parent = book
		sheet.artist = self.request.get('artist')
		sheet.song = self.request.get('song')
		sheet.content = self.request.get('content')
		sheet.put();
		
		self.redirect('/sheets.html?book=' + str(book.key()));
		
class EditSheetHandler(webapp2.RequestHandler):
	
	def get(self):

		user = users.get_current_user()
		
		if user is None:
			self.redirect(users.create_login_url(self.request.uri))
			return
		
		bookKey = Key(self.request.get('book'))
		q = db.GqlQuery("SELECT * FROM Book WHERE __key__ = :1", bookKey)
		book = q.get()
		
		if book is None or book.userid != user.user_id():
			self.redirect('/books.html');
			return
		else:
			
			sheetKey = Key(self.request.get('sheet'))
			q = db.GqlQuery("SELECT * FROM Sheet WHERE __key__ = :1", sheetKey)
			sheet = q.get()
			
			if sheet.author.user_id() == user.user_id():
				
				template_values = {
					'book': book,
					'sheet': sheet
		        }
		
				path = os.path.join(os.path.dirname(__file__), 'edit_sheet.html')
				self.response.out.write(template.render(path, template_values))
				
			else:
				self.redirect('/books.html')
				return		
	
	def post(self):
		
		user = users.get_current_user()
		
		if user is None:
			self.redirect(users.create_login_url(self.request.uri))
			return
		
		bookKey = Key(self.request.get('book'))
		q = db.GqlQuery("SELECT * FROM Book WHERE __key__ = :1", bookKey)
		book = q.get()
		
		if book is None or book.userid != user.user_id():
			self.redirect('/books.html');
			return
		else:
		
			sheetKey = Key(self.request.get('sheet'))
			q = db.GqlQuery("SELECT * FROM Sheet WHERE __key__ = :1", sheetKey)
			sheet = q.get()
			
			if sheet.author.user_id() == user.user_id():
				
				sheet.artist = self.request.get('artist')
				sheet.song = self.request.get('song')
				sheet.content = self.request.get('content')
				sheet.put();
		
				self.redirect('/sheet.html?book=' + str(book.key()) + '&sheet=' + str(sheet.key()));
				return
				
			else:
				self.redirect('/books.html')
				return	
		
	
class SheetHandler(webapp2.RequestHandler):
	
	def get(self):
		
		user = users.get_current_user()
		
		if user is None:
			self.redirect(users.create_login_url(self.request.uri))
			return
		
		bookKey = Key(self.request.get('book'))
		q = db.GqlQuery("SELECT * FROM Book WHERE __key__ = :1", bookKey)
		book = q.get()
		
		if book is None or book.userid != user.user_id():
			self.redirect('/books.html');
			return
		else:
			
			sheetKey = Key(self.request.get('sheet'))
			q = db.GqlQuery("SELECT * FROM Sheet WHERE __key__ = :1", sheetKey)
			sheet = q.get()
		
			template_values = {
				'book': book,
				'sheet': sheet
	        }
	
			path = os.path.join(os.path.dirname(__file__), 'sheet.html')
			self.response.out.write(template.render(path, template_values))

class MySheetsHandler(webapp2.RequestHandler):
	
	def get(self):
		user = users.get_current_user()
		
		if user is None:
			self.redirect(users.create_login_url(self.request.uri))
			return
		
		bookKey = Key(self.request.get('book'))
		q = db.GqlQuery("SELECT * FROM Book WHERE __key__ = :1", bookKey)
		book = q.get()
		
		if book is None or book.userid != user.user_id():
			self.redirect('/books.html');
			return
		else:
			
			sheets = db.GqlQuery("SELECT * FROM Sheet WHERE ancestor is Key(:1)", self.request.get('book'))
			
			template_values = {
				'sheets': sheets,
				'book': book
			}
			
			path = os.path.join(os.path.dirname(__file__), 'sheets.html')
			self.response.out.write(template.render(path, template_values))

class MainHandler(webapp2.RequestHandler):

	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, {}))
		
	def post(self):
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, {}))
		
app = webapp2.WSGIApplication([
							('/', MainHandler), 
							('/sheet', MainHandler), 
							('/sheets.html', MySheetsHandler), 
							('/new_sheet.html', NewSheetHandler),
							('/sheet.html', SheetHandler),
							('/new_book.html', BookHandler),
							('/edit_sheet.html', EditSheetHandler),
							('/books.html', BooksHandler)
							],
                              debug=True)



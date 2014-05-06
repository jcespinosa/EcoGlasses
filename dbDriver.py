#!/usr/bin/python

########################################################################
# This program is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or    #
# at your option) any later version.                                   #
#                                                                      #
# This program is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public License    # 
# along with this program. If not, see <http://www.gnu.org/licenses/>. #
########################################################################

from pymongo import *
from sys import argv

client, db, logos = None, None, None


# ======================================================================
# connect
#
# TODO
#
# ======================================================================
def connect():
  global client, db, collection
  client = MongoClient('localhost', 27017)
  db = client['ecoglasses']
  logos = db['logos']
  return

# ======================================================================
# get
#
# TODO
#
# ======================================================================
def get(name):
  global client, db, collection

  cursor = db.logos.find({'id':name})
  logo = list(cursor)
  logo = logo[0]

  result = dict()
  for key in logo.keys():
    result[key] = str(logo[key])

  return result

# ======================================================================
# main
#
# TODO
#
# ======================================================================
def main():
  logo = argv[1]
  get(logo)
  return

connect()

if(__name__ == '__main__'):
  main()
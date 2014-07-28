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
from traceback import print_exc


# ======================================================================
# DB connection
# ======================================================================
client, db, logos = None, None, None
try:
  print '[!] Attempting to connect to the database... '
  client = MongoClient('localhost', 27017)
  db = client['ecoglasses']
  logos = db['logos']
  print '[O] Connection established with the database.'
except Exception, e:
  print '[X] An error has ocurred while connecting to the database'
  print " Exception >> %s\n" % (e) 
  print_exc()


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


if(__name__ == '__main__'):
  main()

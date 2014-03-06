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

import socket
import threading

from sys import argv, getsizeof


class Socket(threading.Thread):
  def __init__(self, host='localhost', port=9999):
    threading.Thread.__init__(self)
    self.host = host
    self.port = port
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  def close(self):
    print '[O] Connection terminated'
    self.socket.close()
    return


class ServerSocket(Socket):
  def __init__(self, host='localhost', port=9999):
    Socket.__init__(self, host, port)

  def bind(self):
    print '[!] Opening a new socket:'
    print " Host >> %s" % (self.host)
    print " Port >> %d\n" % (self.port)

    try:
      self.socket.bind((self.host, self.port))
    except Exception, e:
      print "[X] An error has ocurred while binding to socket client %s, port %s" % (self.host, self.port)
      print " Exception >> %s\n" % (e)
      return
    finally:
      print '[O] The socket is ready'
      return

  def wait(self):
    print '[>] Waiting for client connection ...'
    self.socket.listen(1)
    self.client, self.host = self.socket.accept()
    print '[O] Connection established'
    return

  def receive(self):
    print '[>] Waiting for client request ...'
    data = ''
    while(True):
      d = self.client.recv(2048)
      if('|END' in d):
        data += d.replace('|END', '')
        break
      data += d
    print "[O] Received %d bytes from client" % (getsizeof(data))
    return data

  def send(self, message):
    print "[>] Sending message to client (%d bytes) ..." % (getsizeof(message))
    self.client.sendall(message)
    return

  def closeClient(self):
    #self.client.shutdown()
    self.client.close()
    return


class ClientSocket(Socket):
  def __init__(self, host="localhost", port=9999):
    Socket.__init__(self, host, port)

  def connect(self):
    print '[!] Attempting to connect to:'
    print " Host >> %s" % (self.host)
    print " Port >> %d\n" % (self.port)

    try:
      self.socket.connect((self.host, self.port))
    except Exception, e:
      print "[X] An error has ocurred while connecting to socket server %s, port %s" % (self.host, self.port)
      print " Exception >> %s\n" % (e)
      return
    finally:
      print '[O] Connection established'
      return

  def receive(self):
    print '[>] Waiting for server response ...'
    data = ''
    while(True):
      d = self.socket.recv(2048)
      if('|END' in d):
        data += d.replace('|END', '')
        break
      data += d
    print "[O] Received %d bytes from server" % (getsizeof(data))
    return data

  def send(self, message):
    print "[>] Sending message to server (%d bytes) ..." % (getsizeof(message))
    self.socket.sendall(message)
    return

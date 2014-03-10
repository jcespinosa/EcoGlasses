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
import zlib

from sys import argv, getsizeof


class Socket(threading.Thread):
  def __init__(self, host='localhost', port=9999):
    threading.Thread.__init__(self)
    self.host = host
    self.port = port
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  def encrypt(self, publicKey, message):
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    key = open(publicKey, 'r').read()
    rsakey = RSA.importKey(key)
    rsakey = PKCS1_OAEP.new(rsakey)
    compressed = zlib.compress(message)
    encrypted = rsakey.encrypt(message)
    eMessage = encrypted.encode('base64')
    return eMessage

  def decrypt(self, privateKey, message):
    from Crypto.PublicKey import RSA 
    from Crypto.Cipher import PKCS1_OAEP 
    from base64 import b64decode 
    key = open(privateKey, 'r').read() 
    rsakey = RSA.importKey(key) 
    rsakey = PKCS1_OAEP.new(rsakey) 
    dMessage = rsakey.decrypt(b64decode(message))
    dMessage = zlib.decompress(dMessage) 
    return dMessage

  def segmentation(self, message, size=200):
    cMessage = [message[i:i+size] for i in range(0, len(message), size)]
    cMessage.reverse()
    return cMessage

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
    
    data, chunk = '', ''
    while('|LAST' not in data):
      while('|END' not in chunk):
        chunk += self.client.recv(512)
      chunk = chunk.replace('|END', '')
      data += self.decrypt('clientPrivateKey', chunk)
      chunk = ''
    data = data.replace('|LAST', '')

    print "[O] Received %d bytes from client" % (getsizeof(data))
    return data

  def send(self, message):
    print "[>] Sending message to client (%d bytes) ..." % (getsizeof(message))
    message = self.compress(message)
    while(len(message) > 1):
      m = self.encrypt('serverPublicKey', message.pop())
      m = m + '|END'
      self.client.sendall(m)
    m = self.encrypt('serverPublicKey', message.pop())
    m = m + '|END|LAST'
    self.client.sendall(m)
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

    data, chunk = '', ''
    while('|LAST' not in data):
      while('|END' not in chunk):
        chunk += self.socket.recv(512)
      chunk = chunk.replace('|END', '')
      data += self.decrypt('serverPrivateKey', chunk)
      chunk = ''
    data = data.replace('|LAST', '')

    print "[O] Received %d bytes from server" % (getsizeof(data))
    return data

  def send(self, message):
    print "[>] Sending message to server (%d bytes) ..." % (getsizeof(message))
    message = self.segmentation(message)
    while(len(message) > 1):
      m = self.encrypt('clientPublicKey', message.pop())
      m = m + '|END'
      self.socket.sendall(m)
    m = self.encrypt('clientPublicKey', message.pop())
    m = m + '|END|LAST'
    self.socket.sendall(m)
    return

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
import zlib

from base64 import b64encode, b64decode
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from sys import getsizeof


# ======================================================================
# Socket
#
#
# ======================================================================
class Socket():
  def __init__(self, host='localhost', port=9999):
    self.host = host
    self.port = port
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  def toFile(self, name, message):
    with open("%s.txt"%(name), 'w+') as out:
      out.write(message)
    return

  def encode(self, message):
    encoded = b64encode(message)
    return encoded

  def decode(self, message):
    decoded = b64decode(message)
    return decoded

  def compress(self, message):
    compressed = zlib.compress(message)
    return compressed

  def decompress(self, message):
    decompressed = zlib.decompress(message)
    return decompressed

  def encrypt(self, message):
    key = open(self.publicKey, 'r').read()
    rsakey = RSA.importKey(key)
    rsakey = PKCS1_OAEP.new(rsakey)
    encrypted = rsakey.encrypt(message)
    return encrypted

  def decrypt(self, message):
    key = open(self.privateKey, 'r').read() 
    rsakey = RSA.importKey(key) 
    rsakey = PKCS1_OAEP.new(rsakey)
    decrypted = rsakey.decrypt(message)
    return decrypted

  def split(self, message, size=100):
    sMessage = self.encode(message)
    sMessage = self.compress(sMessage)
    #sMessage = [sMessage[i:i+size] for i in xrange(0, len(message), size)]
    #sMessage = [self.encrypt(m) for m in sMessage]
    #sMessage = '|END|'.join(sMessage)
    sMessage += '|LAST|'
    return sMessage

  def join(self, message):
    jMessage = message.replace('|LAST|', '')
    #jMessage = jMessage.split('|END|')
    #jMessage = [self.decrypt(m) for m in jMessage]
    #jMessage = ''.join(jMessage)
    jMessage = self.decompress(jMessage)
    jMessage = self.decode(jMessage)
    return jMessage

  def sSend(self, m, message, sender):
    print "[>] Sending message to %s (%d bytes) ..." % (m, getsizeof(message))
    self.toFile("to%s"%(m), message)
    message = self.split(message)
    sender.send(message)
    return

  def sReceive(self, m, receiver):
    print "[>] Waiting for %s ..." % (m)
    data, chunk = '', ''
    while('|LAST|' not in data):
      chunk += receiver.recv(100)
      data += chunk
      chunk = ''
    data = self.join(data)
    self.toFile("from%s"%(m), data)
    print "[O] Received %d bytes from %s." % (getsizeof(data), m)
    return data

  def close(self):
    print '[O] Connection terminated.'
    self.socket.close()
    return


# ======================================================================
# ServerSocket
#
#
# ======================================================================
class ServerSocket(Socket):
  def __init__(self, host='localhost', port=9999):
    Socket.__init__(self, host, port)
    self.publicKey = 'serverPublicKey'
    self.privateKey = 'clientPrivateKey'

  def bind(self):
    print '[!] Opening a new socket:'
    print " Host >> %s" % (self.host)
    print " Port >> %d\n" % (self.port)

    try:
      self.socket.bind((self.host, self.port))
      print '[O] The socket is ready.'
    except Exception, e:
      print "[X] An error has ocurred while binding to socket client %s, port %s." % (self.host, self.port)
      self.port = int(raw_input('New port << '))
      self.socket.bind((self.host, self.port))
      print " Exception >> %s" % (e)
    return

  def wait(self):
    print '[>] Waiting for client connection ...'
    self.socket.listen(1)
    self.client, self.host = self.socket.accept()
    print '[O] Connection established.'
    return

  def send(self, message):
    self.sSend('client', message, self.client)
    return

  def receive(self):
    data = self.sReceive('client', self.client)
    return data

  def closeClient(self):
    self.client.close()
    return


# ======================================================================
# ClientSocket
#
#
# ======================================================================
class ClientSocket(Socket):
  def __init__(self, host='localhost', port=9999):
    Socket.__init__(self, host, port)
    self.publicKey = 'clientPublicKey'
    self.privateKey = 'serverPrivateKey'

  def connect(self):
    print '[!] Attempting to connect to:'
    print " Host >> %s" % (self.host)
    print " Port >> %d" % (self.port)

    try:
      self.socket.connect((self.host, self.port))
      print '[O] Connection established.'
    except Exception, e:
      print "[X] An error has ocurred while connecting to socket server %s, port %s." % (self.host, self.port)
      print " Exception >> %s\n" % (e) 
    return

  def send(self, message):
    self.sSend('server', message, self.socket)
    return

  def receive(self):
    data = self.sReceive('server', self.socket)
    return data

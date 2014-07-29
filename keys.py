from Crypto.PublicKey import RSA 

def generate_RSA(bits=2048):
    '''
    Generate an RSA keypair with an exponent of 65537 in PEM format
    param: bits The key length in bits
    Return private key and public key
    '''
    newKey = RSA.generate(bits, e=65537) 
    publicKey = newKey.publickey().exportKey("PEM") 
    privateKey = newKey.exportKey("PEM") 
    return privateKey, publicKey

def writefile(filename, string):
  with open(filename, 'wb') as output:
    output.write(string)
  return
    
def main():
  clientPrivateKey, clientPublicKey = generate_RSA()
  serverPrivateKey, serverPublicKey = generate_RSA()

  writefile('clientPrivateKey', clientPrivateKey)
  writefile('clientPublicKey', clientPublicKey)
  writefile('serverPrivateKey', serverPrivateKey)
  writefile('serverPublicKey', serverPublicKey)

if(__name__=='__main__'):
  main()

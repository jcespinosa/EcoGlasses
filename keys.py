from sys import argv

def generate_RSA(bits=2048):
    '''
    Generate an RSA keypair with an exponent of 65537 in PEM format
    param: bits The key length in bits
    Return private key and public key
    '''
    from Crypto.PublicKey import RSA 
    new_key = RSA.generate(bits, e=65537) 
    public_key = new_key.publickey().exportKey("PEM") 
    private_key = new_key.exportKey("PEM") 
    return private_key, public_key

def writefile(filename, string):
  f = open(filename, 'wb')
  f.write(string)
  f.close()
    
def main():
  filename = argv[1]

  privateKeyFilename = filename + 'PrivateKey'
  publicKeyFilename = filename + 'PublicKey'

  privatekey, publickey = generate_RSA()

  #print privatekey
  #print publickey

  writefile(privateKeyFilename, privatekey)
  writefile(publicKeyFilename, publickey)

if(__name__=='__main__'):
  main()

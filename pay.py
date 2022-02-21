import codecs, grpc, os
# Generate the following 2 modules by compiling the lnrpc/lightning.proto with the grpcio-tools.
# See https://github.com/lightningnetwork/lnd/blob/master/docs/grpc/python.md for instructions.
import lightning_pb2 as lnrpc, lightning_pb2_grpc as lightningstub
macaroon = codecs.encode(open('/home/carlos/.lnd/data/chain/bitcoin/mainnet/admin.macaroon', 'rb').read(), 'hex')
os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
cert = open('/home/carlos/.lnd/tls.cert', 'rb').read()
ssl_creds = grpc.ssl_channel_credentials(cert)
channel = grpc.secure_channel('localhost:10009', ssl_creds)
stub = lightningstub.LightningStub(channel)
#hacer pago
p_request = ''
def request_generator(p_request):
 
    request = lnrpc.SendRequest(payment_request=p_request)
    yield request
            
request_iterable = request_generator(p_request)
response =  {}
for response in stub.SendPayment(request_iterable, metadata=[('macaroon', macaroon)]):   
    print(response)
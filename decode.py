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

#Decodificar invoice
request = lnrpc.PayReqString(
        pay_req='lnbc40u1pseckpvpp55sx4yzfpr8ty3kmq5jzd7myjp4tl4mzcgwd0shqkps56stnjh6dsdqqcqzpgxqyz5tlsp5nrevc5jrx0shd2awzgkcrt3e3qy2slmtuc6m89ylyuy93wjkd5vs9qyyssqk9udlvs2fc4fyzypst9cyauku3d0pqf4pqee0e5a0uay94v4229szqljp05qa5073lr2gx298dgv7spjp5tnnesw6re3wtxnmawnswgpxhzr99',
    )
response = stub.DecodePayReq(request, metadata=[('macaroon', macaroon)])
print(response)
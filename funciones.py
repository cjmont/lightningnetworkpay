from lndgrpc import LNDClient

lnd = LNDClient(
    "127.0.0.1:10009",
    macaroon_filepath="/home/carlos/.lnd/data/chain/bitcoin/mainnet/admin.macaroon",
    cert_filepath='/home/carlos/.lnd/tls.cert'
)

# Decodificar un PaymentRequest
print('DECODIFICAR UN PAYMENT REQUEST:')
payment_request = ''

try:
  decodificado = lnd.decode_payment_request(payment_request)
  print(decodificado)
except: 
  print("No pudo decodificarse")



# Consultar Saldos de la wallet 
print('SALDOS:')
balance = lnd.wallet_balance()
print(balance)


# Lista de Facturas
print('LISTA DE FACTURAS:')
listafacturas = lnd.list_invoices()
print(listafacturas)


# Ver transacciones
#print('VER TRANSACCIONES:')
#transaccion = lnd.list_transactions()
#print(transaccion)


# Enviar Pago
print('ENVIAR PAGO:')
fee_limit_msat = 1000
payment_request = 'lnbc10u1psux26epp5a2527yxsggm94d9e2ljplv2xx39knuwadlqgpz9ktp2de5q5gazqdq62pe82etzvysx2m3qwe5hvmeqxgcqzpgxqyz5tlsp507qewq6083e4nqhc479pjjdvr8d778qfnspyevvjv2g7le3jtm8s9qyyssqrzlx97ddgjtx0kfg8qccctlh9gv822ewn2rl9ym97sct72k88v638yegx34535vsrchllz8qjhg89snf87adqnhp7hscamyndzcsk4qqjm5aqg'

try:
  enviarpago = lnd.send_payment(payment_request, fee_limit_msat)
  print(enviarpago)
except:
  print("Aqui paso algo malo!")
 
 
 
# Recibir pagos - crear Factura
print('RECIBIR PAGO:')
value = 2500
memo  = 'prueba en vivo'

try:
  recibirpago = lnd.add_invoice(value, memo)
  print(recibirpago)
except:
  print("No hay plata!")

<p>
  <h3>Lighning Network Pagos</h3>
</p>

## Tabla de Contenido

* [Requerimientos](#requerimientos)
* [Configuracion Inicial](#configuracion-inicial)
* [Enviar Pagos](#enviar-pagos)
* [Recibir Pagos - Crear Facturas](#recibir-pagos)



## Requerimientos

* [Python 3.8.3](https://www.python.org/downloads/release/python-383/)
* [lnd-grpc-client](https://github.com/adrienemery/lnd-grpc-client)


* Instalar librerias necesarias:
```sh
/lightning-project$ pip install -r requirements.txt
```

## Flujo de como funcionaria una cartera de pagos lighning:


![flujo](/assets/LightNingFlujo.jpg)


## Configuracion Inicial

* Es importante destacar que se debe contar con un nodo completo Bitcoin y un nodo LightNing sincronizados y funcionando, con sus correspondientes configuraciones de sincronización para que este codigo funcione, ademas debe conectar y luego abrir un canal de pagos. 

* **Conectar un canal de pagos:**<br>
 - Actualmente estos nodos son los mejores conectados sin embargo esto puede cambiar en el futuro.<br>

```sh
paywithmoon.com
lncli connect 025f1456582e70c4c06b61d5c8ed3ce229e6d0db538be337a2dc6d163b0ebc05a5@52.86.210.65:9735

ACINQ
lncli connect 03864ef025fde8fb587d989186ce6a4a186895ee44a926bfc370e2c366597a3f8f@3.33.236.230:9735

Bitrefill
lncli connect 030c3f19d742ca294a55c00376b3b355c3c90d61c6b6b39554dbc7ac19b141c14f@52.50.244.44:9735
```

* **Abrir un canal de pagos:**<br>
`--node_key=` -Es el ID del otro nodo.<br>
`--local_amt=` -Es el monto en satoshis a comprometer dentro del canal, es recomendable actualmente al menos 248 dolares.

```sh
paywithmoon.com
lncli openchannel --node_key=025f1456582e70c4c06b61d5c8ed3ce229e6d0db538be337a2dc6d163b0ebc05a5 --local_amt=561072

ACINQ
lncli openchannel --node_key=03864ef025fde8fb587d989186ce6a4a186895ee44a926bfc370e2c366597a3f8f --local_amt=561072

Bitrefill
lncli openchannel --node_key=030c3f19d742ca294a55c00376b3b355c3c90d61c6b6b39554dbc7ac19b141c14f --local_amt=561072
```

* **Visualizar lista de canales:**<br>
```sh
lncli listchannels
```

* **Ver Balance de los canales:**<br>
```sh
lncli channelbalance
```
* **Ver lista de facturas:**<br>
```sh
lncli listinvoices
```

## Comunicaciones Kafka
Este servicio ahora realiza todas las comunicaciones vía Apache Kafka. Recibe peticiones vía el tópico de entrada, y todos los resultados son enviados via un tópico de salida.
Todos los topicos de kafka en Cryptomarket utilizan dentro de su formato, un inicio con el timestamp y el final de cada mensaje con una firma HMAC-SHA256.
El tópico de salida hacia Celery, es compartido por muchos otros servicios, por lo que el string de "task" debe ser descriptivo, utilizando lightning_ + la tarea ejecutada.

### Input topic: lightning-service
**mensaje:** `timestamp` _(largo 13)_ + `task` _(largo 16)_ + `payment_request` _(largo 400)_ + `signature` _(largo 64)_

### Task:

* **decode**  :     Decodifica un `Payment Request` Devolviendo como respuesta un json que contiene los siguientes valores:<br>
**mensaje:** `timestamp` _(largo 13)_ + `task` _(largo 16)_ + `payment_request` _(largo 400)_ + `signature` _(largo 64)_

**Response:**
```sh
destination: "035e4ff418fc8b5554c5d9eea66396c227bd429a3251c8cbc711002ba215bfc226"
payment_hash: "9e816280c3d93506d4a0ff7199d02252de078e771ec1f0bd352a41cb47e73998"
num_satoshis: 83264
timestamp: 1644368742
expiry: 86399
description: "Pr\303\251stame 36"
cltv_expiry: 40

```

**Mensaje de Salida:**
```sh
    data:{
        "task": "lightning-decode",
        "data": {
        'message': response,
        'status' : 'success'            
        }
    }
```
### Task:

* **pay**  :     Permite hacer un pago a partir de un `Payment Request` Devolviendo como respuesta un json que contiene los siguientes valores:<br>
**mensaje:** `timestamp` _(largo 13)_ + `task` _(largo 16)_ + `payment_request` _(largo 400)_ + `signature` _(largo 64)_

**Response Success:**
```sh
payment_preimage: "\253\234\360\260\250n\376\357\014\231\025z\254\030z\031\002f\3635m\241\3754\030x\016\002\370K*,"
payment_route {
  total_time_lock: 723602
  total_fees: 1
  total_amt: 22001
  hops {
    chan_id: 795470274490400768
    chan_capacity: 261072
    amt_to_forward: 22000
    fee: 1
    expiry: 723562
    amt_to_forward_msat: 22000000
    fee_msat: 1022
    pub_key: "025f1456582e70c4c06b61d5c8ed3ce229e6d0db538be337a2dc6d163b0ebc05a5"
    tlv_payload: true
  }
  hops {
    chan_id: 787317395838533632
    chan_capacity: 20000000
    amt_to_forward: 22000
    expiry: 723562
    amt_to_forward_msat: 22000000
    pub_key: "035e4ff418fc8b5554c5d9eea66396c227bd429a3251c8cbc711002ba215bfc226"
    tlv_payload: true
    mpp_record {
      total_amt_msat: 22000000
      payment_addr: "YM-n\266|3\272\0216%\273B\210\246ns\211`\035`y\t\331\3079\t\222\264R\266d"
    }
  }
  total_fees_msat: 1022
  total_amt_msat: 22001022
}
payment_hash: "\006\215\021Z\337\365\264\237\322\373\274@\257\347\266\032o~!~0l\310F@\"\025\235\375\270\2167"

```

**Response Error (Si la factura ya fue pagada):**
```sh
payment_error: "invoice is already paid"
```
**Response Error (Si el pago no se envio o no hubo ruta por que se puso un fee muy bajo):**
```sh
payment_error: "no_route"
```

**Response Error (Si demoro en enviar o enrutarse):**
```sh
payment_error: "timeout"
```

**Response Error (Si el nodo esta caido o inaccesible):**
```sh
ERROR MESSAGE: failed to connect to all addresses
```

**Mensaje de Salida:**
```sh
    data:{
        "task": "lightning-pay",
        "data": {
        'message': response,
        'status' : 'success'            
        }
    }
```
### Task:

* **create**  :     Permite crear una solicitud de pago o factura generando un `Payment Request` Devolviendo como respuesta un string de al menos 250 carcteres de largo denominado `Payment Request`, El campo `expiry` El cual es la fecha de expiracion de la factura debe ser un numero entero equivalente a segundos:<br>
**mensaje:** `timestamp` _(largo 13)_ + `task` _(largo 16)_ + `amount` _(largo 37)_ + `message` _(largo 37)_ + `expiry` _(largo 37)_ + `signature` _(largo 64)_

**Response:**
```sh
payment_request
```

**Mensaje de Salida:**
```sh
    data:{
        "task": "lightning-create",
        "data": {
        'message': response,
        'status' : 'success'            
        }
    }
```



* Antes de ejecutar cada funcion debe llamarse la ruta del archivo macaroon y el certificado de seguridad estos estan en la ruta de Lightning. Aqui un ejemplo de ennvio y recepcion de pagos funcional hecho con python:

```sh
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
```
## Decodificar Payment Request / Factura

*El `payment_request` es un string largo de mas de 250 caracteres que contiene toda la informacion necesaria para un pago, esta informacion la decodificamos con el siguiente codigo:

```sh
request = lnrpc.PayReqString(
        pay_req='',
    )
response = stub.DecodePayReq(request, metadata=[('macaroon', macaroon)])
print(response)

```


## Recibir Pagos

* Para recibir un pago es necesario crear un `payment_request`:

```sh
request = lnrpc.Invoice(
        memo="17 Febrero",
        value=10039,
        expiry=9200,
    )
response = stub.AddInvoice(request, metadata=[('macaroon', macaroon)])
print(response)
```


## Enviar Pagos

* Para enviar un pago es necesario contar con una factura o id de pago llamado: `payment_request`:

```sh
p_request = ''
def request_generator(p_request):
    request = lnrpc.SendRequest(payment_request=p_request)
    yield request
            
request_iterable = request_generator(p_request)
response =  {}
for response in stub.SendPayment(request_iterable, metadata=[('macaroon', macaroon)]):   
    print(response)
```



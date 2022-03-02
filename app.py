import pdfkit
import psycopg2
from psycopg2 import Error
from jinja2 import Environment, FileSystemLoader
import os
from util.correo import Correo

t_host = "192.168.102.29" 
t_port = "5432"
t_name_db = "switrans"
t_user = "admin"
t_pw = "lITOMUvb7k"
db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_name_db, user=t_user, password=t_pw)
db_cursor = db_conn.cursor()

def Consulta_arrayClientes():
  Sql = " SELECT cl.cliente_codigo, 	cl.cliente_nombre1, substr(now()::text,	1,10) as fechacorte, car.empresa_codigo , te.empresa_nombre,empresa_documento, 	cl.cliente_emailfacturavencer  from tb_factura tf left join tb_cartera car on (car.factura_codigo = tf.factura_codigo) left join tb_carteracambio tc on (tc.cartera_codigo = car.cartera_codigo) left join tb_centrocosto tc2 on (tc2.cencos_codigo = tf.cencos_codigo) left join tb_cliente cl on 	(cl.cliente_codigo = car.cliente_codigo) left join tb_empresa te on	(te.empresa_codigo = tf.empresa_codigo)  where  car.cartera_saldo >= 1	and car.empresa_codigo in (1,2,12) and cl.cliente_excluir is true   group by cl.cliente_codigo,car.empresa_codigo,te.empresa_nombre,empresa_documento  "
  ArrayClientes = []
  ArrayclienteNombre = []
  ArrayFechacorte = []
  ArrayEmpresaNombre = []
  ArrayEmpresaCodigo = []
  ArrayEmpresaDocumento = []
  ArrayClienteEmailfacturavencer = []
  BancosString = ""
  try:
      db_cursor.execute(Sql)
      List_Clientes = db_cursor.fetchall()
      print("---------------------------------  VOY A IMPRIMIR  = "+str(len(List_Clientes))+" PDFs  ---------------------------")
      print("-------------------------------------------------------------------------------------------")
      for i in range(len(List_Clientes)):
        for j in range(0,1):
          ArrayClientes.append(List_Clientes[i][j])
          ArrayclienteNombre.append(List_Clientes[i][j+1])
          ArrayFechacorte.append(List_Clientes[i][j+2])
          ArrayEmpresaCodigo.append(List_Clientes[i][j+3])
          ArrayEmpresaNombre.append(List_Clientes[i][j+4])
          ArrayEmpresaDocumento.append(List_Clientes[i][j+5])
          ArrayClienteEmailfacturavencer.append(List_Clientes[i][j+6])
      for im in range(len(ArrayClientes)):
        cliente_codigo = ArrayClientes[im]
        empresa_codigo = ArrayEmpresaCodigo[im]
        ArrayDatosClientes = {
              'nombreempresa':ArrayEmpresaNombre[im],   
              'cliente_nombre1':ArrayclienteNombre[im],
              'fechacorte':ArrayFechacorte[im], 
        }
        DatosClientes = ArrayDatosClientes
        DatosClientes['empresa_imagen'] = '<img src="../img/'+str(ArrayEmpresaNombre[im])+'.png"/>'
        ArrayFacturas = Consultar_FaturasClientes(cliente_codigo,empresa_codigo)
        DatosClientes['totalestadocuenta'] = ArrayFacturas[0]['Total_cuenta']
        DatosClientes['valorfacturavencidas'] = ArrayFacturas[0]['Saldo_diasvencidos']
        DatosClientes['valorfacturasinvencer'] = ArrayFacturas[0]['Saldo_diasSinvencer']
        DatosClientes['facturas'] = ArrayFacturas
        BancosString = Consultar_BancosEmpresa(empresa_codigo)
        path_abs = os.path.dirname(__file__)
        env = Environment(loader=FileSystemLoader(path_abs +"/template"))
        template = env.get_template( "index.html")
        html = template.render(DatosClientes)
        RutaAbrir = path_abs + "/template/nuevo_html.html"
        f = open(RutaAbrir, 'w')
        f.write(html)
        f.close()
        options = {
            'page-size': 'Letter',
            'orientation': 'Portrait',
            'margin-top': '0.01in',
            'margin-right': '0.50in',
            'margin-bottom': '0.01in',  
            'margin-left': '0.50in',
            'encoding': "UTF-8",
        }
        ClienteNombre = DatosClientes['cliente_nombre1']
        EmpresaNombre = DatosClientes['nombreempresa']
        EmpresaDocumento = ArrayEmpresaDocumento[im]
        print("Imprimiento el pdf del cliente = " + str(ClienteNombre) +" .. El clienteCodigo es " + str(cliente_codigo)+" y para la empresa = " + str(EmpresaNombre) )
        RutaPDf = path_abs +"/pdfs/"
        ruta = (f'{RutaPDf}{cliente_codigo}{"_"}{ArrayEmpresaCodigo[im]}{".pdf"}')
        pdfkit.from_file(RutaAbrir , ruta, options=options)
        recipients = ['david.restrepo@mct.com.co']
        CorreosCopia = ['david.restrepo@mct.com.co']
        ##CorreosCopia = ['deysi.orjuela@mct.com.co','ana.conde@mct.com.co','david.restrepo@mct.com.co']
        correoFuncion = configure_field(ArrayClienteEmailfacturavencer[im])
        ##recipients = CorreosDestino
        print("SE ENVIO EL CORREO A  = " + str(correoFuncion))
        title = "ESTADO DE CARTERA "
        Correo().send_mail(ruta, recipients,CorreosCopia, title, ClienteNombre , EmpresaNombre, EmpresaDocumento,BancosString)
        print("-------------------------------------------------------------------------------------------")
        os.remove(ruta)
  except psycopg2.Error as error:
    print("Error en la connecting a PostgreSQL", error)
  db_cursor.close()
  db_conn.close()

def Consultar_FaturasClientes(List_Clientes,empresa_codigo):

  StringsqlCliente = " SELECT	'E'|| LPAD(cc.cencos_digito, 3, '0')|| '-' || coalesce(f.factura_numerodocumento, f.factura_cencoscodigo::text) as prefijo ,  substr(f.factura_fechacreacion::text,	1,	10)   as fecha_creacion, substr((c.cartera_fechacreacion::date + f.factura_diasvencidos::int)::text,	1,	10)   as fecha_vencimiento,  	c.cartera_saldo as valorfactura,	now()::date-c.cartera_fechacreacion-cl.cliente_diasvencimientofactura as dias_vencidos  from tb_factura f left join tb_facturacambio fc on (f.factura_codigo = fc.factura_codigo and fc.moneda_codigo = 1) left join tb_cartera c on f.factura_codigo = c.factura_codigo left join tb_carteracambio ccam on c.cartera_codigo = ccam.cartera_codigo and ccam.moneda_codigo = 1 left join tb_itemcarteraprod icp on f.factura_codigo = icp.factura_codigo	and coalesce( icp.itemcarteraprod_fechadocumento, icp.itemcarteraprod_fechacreacion::date) <= current_date::date and (icp.itemcarteraprod_anulado = 'NO' or (icp.itemcarteraprod_anulado = 'SI'	and icp.itemcarteraprod_fechaanulacion::date >= current_date::date)) left join tb_itemcarteraprodcambio icpc on f.factura_codigo = icpc.factura_codigo and icpc.moneda_codigo = 1 and icp.itemcarteraprod_codigo = icpc.itemcarteraprod_codigo and icp.itemcarteraprod_subitem = icpc.itemcarteraprod_subitem inner join tb_cliente cl on f.cliente_codigo = cl.cliente_codigo inner join tb_centrocosto cc on (f.cencos_codigo = cc.cencos_codigo) inner join tb_empresa emp on (emp.empresa_codigo = cc.empresa_codigo) inner join tb_estado e on	f.estado_codigo = e.estado_codigo left join tb_vendedor v on f.vendedor_codigo = v.vendedor_codigo left join tb_ciudad cd on f.ciudad_codigo_pago = cd.ciudad_codigo left join tb_ingresocaja ti on icp.documento_codigo = 9 and ti.ingca_codigo = icp.itemcarteraprod_numero left join tb_comprobanteingreso tc on icp.documento_codigo = 31 and tc.coming_codigo = icp.itemcarteraprod_numero and(tc.fecha_anulacion is null or tc.fecha_anulacion::date > current_date ) left join tb_notacontabilidad tn on icp.documento_codigo = 15  and tn.notcon_codigo = icp.itemcarteraprod_numero and (tn.notcon_fecha_anulacion is null or tn.notcon_fecha_anulacion::date > current_date) where f.factura_fechacreacion::date <= current_date and f.estado_codigo in (70, 71, 78, 69, 146) and cl.cliente_codigo =  "
  Stringsqlcliente2 = " group by	f.cencos_codigo,	emp.empresa_codigocontable,	cc.cencos_digito,	f.cliente_codigo,	c.cartera_fechacreacion,	f.factura_codigo,	f.factura_cencoscodigo,	f.factura_cencoscodigo,	f.vendedor_codigo,	c.cartera_saldo,	f.factura_diasvencidos,	ccam.cambio_trm ,	f.factura_fechacreacion::date,	f.estado_codigo,	ccam.cartera_debito,	ccam.cartera_credito,	f.ciudad_codigo_pago,	cl.cliente_diasvencimientofactura,	v.vendedor_nombre,	f.factura_fechacreacion::date having 	(coalesce(ccam.cartera_credito, 0) - SUM((coalesce(icp.itemcarteraprod_multiplicador, 0) * coalesce(icpc.cambio_trm, 0) * coalesce(case when icp.itemcarteraprod_anulado <> 'SI' and coalesce ( ti.ingca_fechacreacion::date , tc.coming_fecha::date, tn.notcon_fechacreacion::date) <= current_date::date then icpc.itemcarteraprod_valor else 0 end, 0) )) ) >1 order by	dias_vencidos desc"
  postgreSQL_cliente = ( f' {StringsqlCliente}{List_Clientes}{" and c.empresa_codigo =  "}{empresa_codigo}{Stringsqlcliente2} ' )
  try:
    cursor = db_conn.cursor()
    cursor.execute(postgreSQL_cliente)
    row = cursor.fetchone()
    header = [i[0] for i in cursor.description]
    rowarray_list  = []
    Total_cuenta = 0
    Saldo_diasvencidos = 0
    Saldo_diasSinvencer = 0
    while row is not None:
        Total_cuenta = Total_cuenta + row[3]
        if row[4] > 0 :
          Saldo_diasvencidos =Saldo_diasvencidos + row[3]
        elif row[4] <= 0:
          Saldo_diasSinvencer = Saldo_diasSinvencer + row[3]
        t = { 
            header[0]:row[0], 
            header[1]:row[1], 
            header[2]:row[2], 
            header[3]:("{:,.2f}".format(row[3])),
            header[4]:row[4], 
        }
        rowarray_list.append(t)
        row = cursor.fetchone()
    w = {
      'Total_cuenta' : ("{:,.2f}".format(Total_cuenta)),
      'Saldo_diasvencidos': ("{:,.2f}".format(Saldo_diasvencidos)),
      'Saldo_diasSinvencer': ("{:,.2f}".format(Saldo_diasSinvencer)),
    }
    return(w,rowarray_list)
  except (Exception, Error) as error:
      print("Error while connecting to PostgreSQL", error)
  db_cursor.close()
  db_conn.close()

def Consultar_BancosEmpresa(empresa_codigo):
  Sql= "SELECT b.banco_nombre || '     /   Cuenta Corriente - No.  ' ||banco_cta as cuenta"
  SqlBancos =( f' {Sql}{"  from tb_empresa em left join tb_banco b on (em.empresa_codigo=b.empresa_codigo) where b.banco_envio=true and em.empresa_codigo =  "}{empresa_codigo}' )
  Respuesta =""
  try:
    db_cursor.execute(SqlBancos)
    row = db_cursor.fetchone()
    while row is not None:
      Respuesta = Respuesta +row[0] + " <br> "
      row = db_cursor.fetchone()
    return(Respuesta)
  except (Exception, Error) as error:
    print("Error en la connections  a PostgreSQL !!!!", error)
  db_cursor.close()
  db_conn.close()

def configure_field(field):
  if field == '':
    x = 'sincorreo@mct.com.co'
  else:
    x = (field.split(','))
  return x 

Consulta_arrayClientes()
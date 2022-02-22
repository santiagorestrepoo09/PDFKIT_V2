import pdfkit
import psycopg2
from psycopg2 import Error
from jinja2 import Environment, FileSystemLoader
import os

t_host = "192.168.102.29" 
t_port = "5432"
t_name_db = "switrans"
t_user = "admin"
t_pw = "lITOMUvb7k"
db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_name_db, user=t_user, password=t_pw)
db_cursor = db_conn.cursor()

def Consulta_arrayClientes():
  Sql = " SELECT cl.cliente_codigo,car.empresa_codigo , te.empresa_nombre  from tb_factura tf left join tb_cartera car on (car.factura_codigo = tf.factura_codigo) left join tb_carteracambio tc on (tc.cartera_codigo = car.cartera_codigo) left join tb_centrocosto tc2 on (tc2.cencos_codigo = tf.cencos_codigo) left join tb_cliente cl on 	(cl.cliente_codigo = car.cliente_codigo) left join tb_empresa te on	(te.empresa_codigo = tf.empresa_codigo) where  car.cartera_saldo >= 1 and car.empresa_codigo = 1 group by cl.cliente_codigo,car.empresa_codigo,te.empresa_nombre  "
  ArrayClientes = []
  ArrayEmpresaNombre = []
  ArrayEmpresaCodigo = []
  try:
      db_cursor.execute(Sql)
      List_Clientes = db_cursor.fetchall()
      print("Voy a imprimir  = "+str(len(List_Clientes))+" PDFs")
      for i in range(len(List_Clientes)):
        for j in range(0,1):
          ArrayClientes.append(List_Clientes[i][j])
          ArrayEmpresaCodigo.append(List_Clientes[i][j+1])
          ArrayEmpresaNombre.append(List_Clientes[i][j+2])
      #print(ArrayClientes)
      #print(ArrayEmpresaCodigo)
      ##print(ArrayEmpresaNombre)
      for im in range(len(ArrayClientes)):
        cliente_codigo = ArrayClientes[im]
        empresa_codigo = ArrayEmpresaCodigo[im]
        DatosClientes = Consultar_DatosClientes(cliente_codigo,empresa_codigo)
        print('<img src="../img/'+str(ArrayEmpresaNombre[im])+'.png"/>')
        DatosClientes['empresa_imagen'] = '<img src="../img/'+str(ArrayEmpresaNombre[im])+'.png"/>'
        DatosClientes['facturas'] = Consultar_FaturasClientes(cliente_codigo,empresa_codigo)
        #print(ArrayClientes[im])
        #print(ArrayEmpresaCodigo[im])
        print("Imprimiento el pdf del cliente =  " + str(cliente_codigo)+" y para la empresa = " + str(ArrayEmpresaCodigo[im]))
        print("------------------------------------------------------------------------------")
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
        RutaPDf = path_abs +"/pdfs/"
        ruta = (f'{RutaPDf}{cliente_codigo}{"_"}{ArrayEmpresaCodigo[im]}{".pdf"}')
        pdfkit.from_file(RutaAbrir , ruta, options=options)
  except psycopg2.Error as error:
    print("Error en la connecting a PostgreSQL", error)
  db_cursor.close()
  db_conn.close()

def Consultar_DatosClientes(List_Clientes,empresa_codigo):
  Sql2 = (f'{"SELECT te.empresa_nombre as nombreEmpresa,	cl.cliente_nombre1, substr(now()::text,	1,	10) as fechacorte,	sum(fc.factura_total) as TotalEstadoCuenta,	(	select	case	when sum(fc.factura_total) is null then 0 else sum(fc.factura_total) end as ValorFacturaVencidas from tb_factura ft	left join tb_cartera car on (car.factura_codigo = ft.factura_codigo) left join tb_carteracambio tc on (tc.cartera_codigo = car.cartera_codigo) left join tb_cliente cl on (cl.cliente_codigo = car.cliente_codigo) left join tb_facturacambio fc on (ft.factura_codigo = fc.factura_codigo) where cl.cliente_codigo = "}{List_Clientes}{" 	and car.empresa_codigo ="}{empresa_codigo}{"	and now()::date-car.cartera_fechacreacion-cl.cliente_diasvencimientofactura > 0 and tc.cartera_saldo >=1), (select case when sum(fc.factura_total) is null then 0 else sum(fc.factura_total) end as ValorFacturaSinVencer from tb_factura ft left join tb_cartera car on (car.factura_codigo = ft.factura_codigo) left join tb_carteracambio tc on (tc.cartera_codigo = car.cartera_codigo) left join tb_cliente cl on (cl.cliente_codigo = car.cliente_codigo) left join tb_facturacambio fc on (ft.factura_codigo = fc.factura_codigo) where cl.cliente_codigo = "}{List_Clientes}{" and car.empresa_codigo ="}{empresa_codigo}{"and now()::date-car.cartera_fechacreacion-cl.cliente_diasvencimientofactura <= 0 and tc.cartera_saldo >=1) from tb_factura tf left join tb_cartera car on (car.factura_codigo = tf.factura_codigo) left join tb_cliente cl on (cl.cliente_codigo = car.cliente_codigo) left join tb_carteracambio tc on (tc.cartera_codigo = car.cartera_codigo) left join tb_empresa te on (te.empresa_codigo = tf.empresa_codigo) left join tb_facturacambio fc on (tf.factura_codigo = fc.factura_codigo) where car.cliente_codigo = "}{List_Clientes}{" and car.empresa_codigo ="}{empresa_codigo}{"and car.cartera_saldo >= 1 group by te.empresa_nombre, cl.cliente_nombre1"} ')
  try:
      db_cursor.execute(Sql2)
      row = db_cursor.fetchone()
      while row is not None:
          rowarray_list = {
              'nombreempresa':row[0],   
              'cliente_nombre1':row[1],
              'fechacorte':row[2], 
              'totalestadocuenta':("{:,.2f}".format(row[3])), 
              'valorfacturavencidas':("{:,.2f}".format(row[4])),
              'valorfacturasinvencer':("{:,.2f}".format(row[5])), 
          }
          row = db_cursor.fetchone()
      return(rowarray_list)
  except (Exception, Error) as error:
    print("Error en la connections  a PostgreSQL !!!!", error)
  db_cursor.close()
  db_conn.close()


def Consultar_FaturasClientes(List_Clientes,empresa_codigo):

  StringsqlCliente = " SELECT	LPAD(emp.empresa_codigocontable, 2, '0')|| LPAD(cc.cencos_digito, 3, '0')|| '-' || coalesce(f.factura_numerodocumento, f.factura_cencoscodigo::text) as prefijo ,  substr(f.factura_fechacreacion::text,	1,	10)   as fecha_creacion, substr((c.cartera_fechacreacion::date + f.factura_diasvencidos::int)::text,	1,	10)   as fecha_vencimiento,  	fc.factura_total as valorfactura,	now()::date-c.cartera_fechacreacion-cl.cliente_diasvencimientofactura as dias_vencidos  from tb_factura f left join tb_facturacambio fc on (f.factura_codigo = fc.factura_codigo and fc.moneda_codigo = 1) left join tb_cartera c on f.factura_codigo = c.factura_codigo left join tb_carteracambio ccam on c.cartera_codigo = ccam.cartera_codigo and ccam.moneda_codigo = 1 left join tb_itemcarteraprod icp on f.factura_codigo = icp.factura_codigo	and coalesce( icp.itemcarteraprod_fechadocumento, icp.itemcarteraprod_fechacreacion::date) <= current_date::date and (icp.itemcarteraprod_anulado = 'NO' or (icp.itemcarteraprod_anulado = 'SI'	and icp.itemcarteraprod_fechaanulacion::date >= current_date::date)) left join tb_itemcarteraprodcambio icpc on f.factura_codigo = icpc.factura_codigo and icpc.moneda_codigo = 1 and icp.itemcarteraprod_codigo = icpc.itemcarteraprod_codigo and icp.itemcarteraprod_subitem = icpc.itemcarteraprod_subitem inner join tb_cliente cl on f.cliente_codigo = cl.cliente_codigo inner join tb_centrocosto cc on (f.cencos_codigo = cc.cencos_codigo) inner join tb_empresa emp on (emp.empresa_codigo = cc.empresa_codigo) inner join tb_estado e on	f.estado_codigo = e.estado_codigo left join tb_vendedor v on f.vendedor_codigo = v.vendedor_codigo left join tb_ciudad cd on f.ciudad_codigo_pago = cd.ciudad_codigo left join tb_ingresocaja ti on icp.documento_codigo = 9 and ti.ingca_codigo = icp.itemcarteraprod_numero left join tb_comprobanteingreso tc on icp.documento_codigo = 31 and tc.coming_codigo = icp.itemcarteraprod_numero and(tc.fecha_anulacion is null or tc.fecha_anulacion::date > current_date ) left join tb_notacontabilidad tn on icp.documento_codigo = 15  and tn.notcon_codigo = icp.itemcarteraprod_numero and (tn.notcon_fecha_anulacion is null or tn.notcon_fecha_anulacion::date > current_date) where f.factura_fechacreacion::date <= current_date and f.estado_codigo in (70, 71, 78, 69, 146) and cl.cliente_codigo =  "
  Stringsqlcliente2 = " group by	f.cencos_codigo,	emp.empresa_codigocontable,	cc.cencos_digito,	f.cliente_codigo,	c.cartera_fechacreacion,	f.factura_codigo,	f.factura_cencoscodigo,	f.factura_cencoscodigo,	f.vendedor_codigo,	fc.factura_total,	f.factura_diasvencidos,	ccam.cambio_trm ,	f.factura_fechacreacion::date,	f.estado_codigo,	ccam.cartera_debito,	ccam.cartera_credito,	f.ciudad_codigo_pago,	cl.cliente_diasvencimientofactura,	v.vendedor_nombre,	f.factura_fechacreacion::date having 	(coalesce(ccam.cartera_credito, 0) - SUM((coalesce(icp.itemcarteraprod_multiplicador, 0) * coalesce(icpc.cambio_trm, 0) * coalesce(case when icp.itemcarteraprod_anulado <> 'SI' and coalesce ( ti.ingca_fechacreacion::date , tc.coming_fecha::date, tn.notcon_fechacreacion::date) <= current_date::date then icpc.itemcarteraprod_valor else 0 end, 0) )) ) >1 order by	dias_vencidos desc"
  postgreSQL_cliente = ( f' {StringsqlCliente}{List_Clientes}{" and c.empresa_codigo =  "}{empresa_codigo}{Stringsqlcliente2} ' )
  try:
    cursor = db_conn.cursor()
    cursor.execute(postgreSQL_cliente)
    row = cursor.fetchone()
    header = [i[0] for i in cursor.description]
    rowarray_list  = []
    while row is not None:
        t = { 
            header[0]:row[0], 
            header[1]:row[1], 
            header[2]:row[2], 
            header[3]:("{:,.2f}".format(row[3])),
            header[4]:row[4], 
        }
        rowarray_list.append(t)
        row = cursor.fetchone()
    return(rowarray_list)
  except (Exception, Error) as error:
      print("Error while connecting to PostgreSQL", error)
  db_cursor.close()
  db_conn.close()

Consulta_arrayClientes()
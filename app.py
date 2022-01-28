import pdfkit
import psycopg2
from psycopg2 import Error
from jinja2 import Environment, FileSystemLoader

t_host = "192.168.102.24" 
t_port = "5432"
t_name_db = "switrans"
t_user = "admin"
t_pw = "lITOMUvb7k"
db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_name_db, user=t_user, password=t_pw)
db_cursor = db_conn.cursor()

def Consulta_arrayClientes(rutacss = ''):
  Sql = "SELECT cl.cliente_codigo,car.empresa_codigo , te.empresa_nombre  from tb_factura tf left join tb_cartera car on (car.factura_codigo = tf.factura_codigo) left join tb_carteracambio tc on (tc.cartera_codigo = car.cartera_codigo) left join tb_centrocosto tc2 on (tc2.cencos_codigo = tf.cencos_codigo) left join tb_cliente cl on 	(cl.cliente_codigo = car.cliente_codigo) left join tb_empresa te on	(te.empresa_codigo = tf.empresa_codigo) where  car.cartera_saldo >= 1 group by cl.cliente_codigo,car.empresa_codigo,te.empresa_nombre  "
  ArrayClientes = []
  ArrayEmpresaNombre = []
  ArrayEmpresaCodigo = []
  try:
      db_cursor.execute(Sql)
      List_Clientes = db_cursor.fetchall()
      #print(List_Clientes)
      for i in range(len(List_Clientes)):
        for j in range(0,1):
          ArrayClientes.append(List_Clientes[i][j])
          ArrayEmpresaCodigo.append(List_Clientes[i][j+1])
          ArrayEmpresaNombre.append(List_Clientes[i][j+2])
      print(ArrayClientes)
      print(ArrayEmpresaCodigo)
      print(ArrayEmpresaNombre)
      for im in range(len(ArrayClientes)):
        cliente_codigo = ArrayClientes[im]
        empresa_codigo = ArrayEmpresaCodigo[im]
        DatosClientes = Consultar_DatosClientes(cliente_codigo,empresa_codigo)
        print('<img src="../img/'+str(ArrayEmpresaNombre[im])+'.png"/>')
        DatosClientes['empresa_imagen'] = '<img src="../img/'+str(ArrayEmpresaNombre[im])+'.png"/>'
        DatosClientes['facturas'] = Consultar_FaturasClientes(cliente_codigo,empresa_codigo)
        print(ArrayClientes[im])
        print(ArrayEmpresaCodigo[im])
        print("Entro a generar")
        env = Environment(loader = FileSystemLoader("template"))
        template =  env.get_template("index.html")
        html = template.render(DatosClientes)
        f = open('template/nuevo_html.html','w')
        f.write(html)
        f.close()
        options = {
            'page-size' : 'Letter',
            'orientation' : 'Portrait',
            'margin-top': '0.01in',
            'margin-right': '0.50in',
            'margin-bottom': '0.01in',
            'margin-left': '0.50in',
            'encoding': "UTF-8",
        }
        ruta = (f'{"/home/santiago/Escritorio/DEVELOP/PYTHON/Pdfkit/pdfs/"}{cliente_codigo}{"_"}{ArrayEmpresaCodigo[im]}{".pdf"}')
        pdfkit.from_file('template/nuevo_html.html' , ruta, options=options)
  except psycopg2.Error as error:
    print("Error en la connecting a PostgreSQL", error)
  db_cursor.close()
  db_conn.close()

def Consultar_DatosClientes(List_Clientes,empresa_codigo):
  print("inicio recorrer el Datos clientes")
  Sql2 = ( f' { " select	te.empresa_nombre as nombreEmpresa,	cl.cliente_nombre1,  substr(now()::text,1,10) as fechacorte,	sum(tc.cartera_saldo) as TotalEstadoCuenta,	(select sum(tc.cartera_saldo) as ValorFacturaVencidas from tb_factura ft left join tb_cartera car on (car.factura_codigo = ft.factura_codigo) left join tb_carteracambio tc on (tc.cartera_codigo = car.cartera_codigo) left join tb_cliente cl on	(cl.cliente_codigo = car.cliente_codigo) where 	cl.cliente_codigo = "}{List_Clientes}{" and car.empresa_codigo = "}{empresa_codigo}{" and now()::date-car.cartera_fechacreacion-cl.cliente_diasvencimientofactura > 0 ),	(select sum(tc.cartera_saldo) as ValorFacturaSinVencer from tb_factura ft left join tb_cartera car on (car.factura_codigo = ft.factura_codigo) left join tb_carteracambio tc on (tc.cartera_codigo = car.cartera_codigo) left join tb_cliente cl on	(cl.cliente_codigo = car.cliente_codigo) where 	cl.cliente_codigo = "}{List_Clientes}{" and car.empresa_codigo = "}{empresa_codigo}{" and now()::date-car.cartera_fechacreacion-cl.cliente_diasvencimientofactura <= 0 )from tb_factura tf left join tb_cartera car on	(car.factura_codigo = tf.factura_codigo) 	left join tb_cliente cl on (cl.cliente_codigo = car.cliente_codigo)  left join tb_carteracambio tc on (tc.cartera_codigo = car.cartera_codigo) left join tb_empresa te on(te.empresa_codigo=tf.empresa_codigo) where car.cliente_codigo = "}{List_Clientes}{" and car.empresa_codigo = "}{empresa_codigo}{" and car.cartera_saldo >= 1  GROUP by te.empresa_nombre,cl.cliente_nombre1"}'	)
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
  print("inicio recorrer Facturas Clientes")
  StringSqlInicial = " SELECT	tf.factura_empresaprefijo || '' || tc2.cencos_digito || '-' || factura_numerodocumento as prefijo, substr(factura_fechacreacion::text,1,10) as fecha_creacion, 	cast((car.cartera_fechacreacion + cl.cliente_diasvencimientofactura) as text) as fecha_vencimiento,	tc.cartera_saldo as saldo,	now()::date-car.cartera_fechacreacion-cl.cliente_diasvencimientofactura as dias_vencidos from tb_factura tf left join tb_cartera car on	(car.factura_codigo = tf.factura_codigo) left join tb_carteracambio tc on (tc.cartera_codigo = car.cartera_codigo) left join tb_centrocosto tc2 on (tc2.cencos_codigo = tf.cencos_codigo) left join tb_cliente cl on (cl.cliente_codigo = car.cliente_codigo) where car.cliente_codigo = "
  postgreSQL_cliente = ( f' {StringSqlInicial}{List_Clientes}{" and car.empresa_codigo = "}{empresa_codigo}{" and car.cartera_saldo >= 1  order by dias_vencidos desc"} ' )
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

if __name__=="__main__":
  rutacss = '/home/santiago/Escritorio/DEVELOP/PYTHON/Pdfkit/template/style.css'
  Consulta_arrayClientes(rutacss)
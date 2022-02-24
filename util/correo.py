from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from datetime import datetime
from email.utils import formatdate
import smtplib

class Correo:

    current_date = datetime.today().strftime('%Y-%m-%d')

    def send_mail(self,ruta, destinatarios, title,ClienteNombre, EmpresaNombre,EmpresaCodigo):
        print("Ingresa a Enviar Correo!!!!!")

        server = smtplib.SMTP(host='correo.mct.com.co',port=25)
        msg = MIMEMultipart()
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(ruta, "rb").read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="Informe_Facturas_Vencer.pdf"')
        msg.attach(part)

        password = "temporal_2015"
        msg['From'] = "notificaciones@mct.com.co"
        msg['To'] = ",".join(destinatarios)
        msg['Date'] = formatdate(localtime = True)
        msg['Subject'] = title + self.current_date


        if EmpresaCodigo == 1:
          nit = "830.004.861-4"
          Cuenta_BancoBogota = "920029113"
          Cuenta_BancoBancolombia = "03100032005"       
        elif EmpresaCodigo == 2:
          nit = "806.002.953-7"
          Cuenta_BancoBogota = "055063218"
          Cuenta_BancoBancolombia = "16700000442"
        elif EmpresaCodigo == 12:
          nit = "901.051.109-0"
          Cuenta_BancoBogota = "920029113"
          Cuenta_BancoBancolombia = "16700000442"

        mail_body = self.set_mail_body(ClienteNombre, EmpresaNombre,nit,Cuenta_BancoBogota,Cuenta_BancoBancolombia)
        server.starttls()
        server.login(msg['From'], password)
        msg.attach(mail_body)
        server.sendmail(msg['From'], destinatarios, msg.as_string())
        server.quit()

        print("Correo enviado con exito %s:" % (msg['To']))

    def set_mail_body(sef,ClienteNombre,EmpresaNombre,nit,Cuenta_BancoBogota,Cuenta_BancoBancolombia):
        body_html = f"""\
                <html>
                  <head></head>
                  <body>
                    <tr> 
                      <td><font SIZE='6'> Apreciado Cliente, </font></td>
                    </tr>
                    <tr>
                      <td><font SIZE='10'><b> {ClienteNombre} </b></font></td>
                    </tr>
                    <br>
                    <tr>
                      <td><font SIZE='4'> Adjunto le enviamos el estado de cartera con corte al día de hoy de sus operaciones realizadas con la Empresa ( {EmpresaNombre} ). </font></td>
                    </tr>
                    <br>
                    <tr>
                      <td><font SIZE='4' Agradecemos realice sus pagos a través de transferencia a nuestras cuentas: </font></td>
                    </tr>
                    <br>
                    <tr>
                      <td><font SIZE='12'><b>{EmpresaNombre} </br></font></td>
                    </tr>
                    <tr>
                      <td bgcolor='yellow'><font SIZE='3'><b>Nit No. {nit} </b></font></td>
                    </tr>
                    <br>
                    <tr>
                      <td <font SIZE='3'> Banco de Bogotá - Cuenta Corriente No. {Cuenta_BancoBogota}</font></td>
                    </tr>
                    <tr>
                      <td><font SIZE='3'> Bancolombia – Cuenta Corriente No. {Cuenta_BancoBancolombia}</font></td>
                    </tr>

                    <br>
                    <br>
                    <br>
                    <tr>
                      <td><font SIZE='4'>Cualquier inquietud puede comunicarse con nosotros al correo electrónico cartera@mct.com.co </font></td>
                    </tr>
                    <tr>
                      <td><font SIZE='4'>Cordialmente. </font></td>
                    </tr>
                    <br>
                    <br>
                    <tr>
                      <td><font SIZE='5'><b>Proceso de Facturación y Cartera   </br></font></td>
                    </tr>
                    <tr>
                      <td><font SIZE='4'>Empresa ( {EmpresaNombre} )   </font></td>
                    </tr>
                    <tr>
                      <td><font SIZE='5'><b>Tel.Fijo No.: (57) 601 821 90 82 Ext.: 4705 – 4706</br></font></td>
                    </tr>  
                    <tr>
                      <td><font SIZE='5'><b>Celular No 323 311 35 00 </br></font></td>
                    </tr>
                    <br>
                    <br>
                    <tr>
                      <td><font SIZE='5'><b>Oficinas Principales - Parque Logístico MCT </br></font></td>
                    </tr>
                    <tr>
                      <td><font SIZE='4'>Vía La Argentina - Vereda La Isla, Lote La Adelia No. 2 </font></td>
                    </tr>
                    <tr>
                      <td><font SIZE='4'>Funza – Cundinamarca </font></td>
                    </tr>
                    
                  </body>
                </html>
                """
        part = MIMEText(body_html, 'html')
        return part

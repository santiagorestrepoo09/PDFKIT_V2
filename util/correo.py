from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from datetime import datetime
from email.utils import formatdate
import smtplib

class Correo:

    current_date = datetime.today().strftime('%Y-%m-%d')

    def send_mail(self,ruta, destinatarios,CorreosCopia, title,ClienteNombre, EmpresaNombre,EmpresaDocumento,BancosString):
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
        msg['Cc'] = ",".join(CorreosCopia)
        msg['Date'] = formatdate(localtime = True)
        msg['Subject'] = title + ", " + ClienteNombre + " - fecha ( " + self.current_date +" )"
      
        enviarCorreos = destinatarios + CorreosCopia

        mail_body = self.set_mail_body(ClienteNombre, EmpresaNombre,EmpresaDocumento,BancosString)
        server.starttls()
        server.login(msg['From'], password)
        msg.attach(mail_body)
        server.sendmail(msg['From'], enviarCorreos, msg.as_string())
        server.quit()

        print("Correo enviado con exito %s:" % (msg['To']))
        print("Correo con copia a  %s:" % (msg['Cc']))

    def set_mail_body(sef,ClienteNombre,EmpresaNombre,EmpresaDocumento,BancosString):
        body_html = f"""\
                <html>
                  <head></head>
                  <body>
                    <tr> 
                      <td><font SIZE='6'> Apreciado Cliente,  <b> {ClienteNombre} </b> </font></td>
                    </tr>
                    <br>
                    <tr>
                      <td><font SIZE='4'> Nos permitimos compartir el estado general de la cartera para su análisis y programación.  </font></td>
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
                      <td><font SIZE='12'><b>{EmpresaNombre} <br>  Nit No. {EmpresaDocumento}  </b></font></td>
                    </tr>
                    <br>
                    <tr>
                      <td <font SIZE='4'> {BancosString} <br> </font></td>
                    </tr>
                    <br>
                    <tr>
                      <td><font SIZE='4'> Si a la fecha de corte de este extracto, usted ha cancelado alguno de los documentos relacionados, agradecemos nos envíe el soporte de pagos al correo electrónico cartera@mct.com.co y/o facturacion@mct.com.co , para actualizar su estado de cuenta de manera inmediata.  </font></td>
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

import azure.functions as func
import logging
from email.message import EmailMessage
import smtplib
import http.client
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="HttpMailSender")
def HttpMailSender(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Configuración de las credenciales de correo
        mailerAccount = "user1@outlook.com"
        mailerPassword = "Password"
        receiverAccount = "user2@outlook.com"
        message = "A sync from any of your connections fails"

        # Obtener el destinatario personalizado, si se proporciona
        mailTo = req.params.get("mailTo")
        if mailTo:
            receiverAccount = mailTo

        # Obtener el mensaje personalizado, si se proporciona
        req_body = req.get_json()
        message = req_body.get("text", message)

        # Crear el objeto EmailMessage
        email = EmailMessage()
        email["From"] = mailerAccount
        email["To"] = receiverAccount
        email["Subject"] = "Failed syncs"
        email.set_content(message)

        # Uncomment this if you are using gmail on SMTP
        # smtp = smtplib.SMTP_SSL("smtp.gmail.com")

        # Uncomment this if you are using outlook
        smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
        smtp.starttls()

        smtp.login(mailerAccount, mailerPassword)
        smtp.sendmail(mailerAccount, receiverAccount, email.as_string())
        smtp.quit()

        # Datos para la petición POST
        url = "m365x34045766.webhook.office.com"
        path = "/webhookb2/15bff0f2-d9f6-4f63-acd6-0e8947873dc6@8616c0a8-5ee2-493d-8402-b573776838d6/IncomingWebhook/7e46b2c8e5d940dfb9ace7b65e834d82/72974983-3e0c-40d9-ac0d-441d828dc3dc"

        # Crear una conexión HTTP
        conn = http.client.HTTPSConnection(url)

        # Datos para la petición POST
        headers = {"Content-Type": "application/json"}
        data = req_body  # Utilizar directamente el cuerpo de la solicitud JSON
        data_json = json.dumps(data)

        # Hacer la petición POST
        conn.request("POST", path, data_json, headers)

        # Obtener la respuesta
        response = conn.getresponse()
        logging.info("Response status: %s %s", response.status, response.reason)
        response_content = response.read().decode("utf-8")
        logging.info("Response content: %s", response_content)

        # Verificar si la petición fue exitosa (código de estado 200)
        if response.status == 200:
            return func.HttpResponse("Petición POST exitosa", status_code=200)
        else:
            return func.HttpResponse(
                "Error en la petición POST", status_code=response.status
            )
    except Exception as e:
        return func.HttpResponse(f"Error: {e}", status_code=500)

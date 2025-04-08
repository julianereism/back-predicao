from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import random, smtplib, ssl
from email.message import EmailMessage

app = FastAPI()

# Dados esperados
class EmailRequest(BaseModel):
    email: EmailStr

# Função de envio
def enviar_email(destinatario, codigo):
    remetente = "seuemail@gmail.com"
    senha_app = "sua_senha_de_app"

    msg = EmailMessage()
    msg.set_content(f"Seu código é: {codigo}")
    msg["Subject"] = "Código de Verificação"
    msg["From"] = remetente
    msg["To"] = destinatario

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as servidor:
            servidor.login(remetente, senha_app)
            servidor.send_message(msg)
        return True
    except Exception as e:
        print(e)
        return False

# Endpoint
@app.post("/enviar_codigo")
def enviar_codigo(dados: EmailRequest):
    codigo = str(random.randint(100000, 999999))
    sucesso = enviar_email(dados.email, codigo)

    if sucesso:
        return {"status": "ok", "codigo": codigo}
    else:
        raise HTTPException(status_code=500, detail="Erro ao enviar e-mail")

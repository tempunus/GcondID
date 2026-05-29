# GcondID

Aplicacao web Django para gestao administrativa de condominios, com usuarios aprovados por administrador, estoque setorizado, chamados de manutencao, dashboard e relatorios em PDF/Excel.

## Como rodar

```powershell
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`.

## Banco de dados

O projeto nao usa MySQL. Use PostgreSQL em producao ou SQLite apenas para desenvolvimento local.

```powershell
$env:DATABASE_URL="postgres://usuario:senha@localhost:5432/gcondid"

```

## Modulos

- `users`: cadastro, login por email, aprovacao, bloqueio e niveis de acesso.
- `estoque`: itens por setor, entrada, baixa e logs automaticos.
- `chamados`: abertura, fotos, status, tecnico, solucao e conclusao.
- `dashboard`: cards clicaveis e movimentacoes recentes.
- `relatorios`: exportacoes PDF e Excel.

## Notificacoes de chamados

Ao abrir um chamado, selecione o usuario responsavel. O sistema envia email pelo backend configurado no Django e registra uma tentativa de WhatsApp.

Em desenvolvimento, o email usa `console.EmailBackend` e aparece no terminal. Para SMTP real, configure:

```powershell
$env:EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
$env:EMAIL_HOST="smtp.seudominio.com"
$env:EMAIL_PORT="587"
$env:EMAIL_HOST_USER="usuario"
$env:EMAIL_HOST_PASSWORD="senha"
$env:EMAIL_USE_TLS="true"
$env:DEFAULT_FROM_EMAIL="GcondID <nao-responda@seudominio.com>"
```

Para WhatsApp automatico pela API oficial da Meta, configure as variaveis abaixo antes de iniciar o servidor. O telefone do usuario responsavel deve estar no cadastro do usuario em formato internacional, apenas numeros, por exemplo `5511999999999`.

```powershell
$env:WHATSAPP_PROVIDER="meta"
$env:WHATSAPP_META_API_VERSION="v25.0"
$env:WHATSAPP_META_PHONE_NUMBER_ID="ID_DO_NUMERO_NO_WHATSAPP_BUSINESS"
$env:WHATSAPP_META_ACCESS_TOKEN="TOKEN_DE_ACESSO_DA_META"
python manage.py runserver
```

Quando um chamado for aberto ou tiver o responsavel alterado, o sistema envia um texto para o WhatsApp do responsavel e grava o resultado em `TicketNotification`.

Como alternativa, voce tambem pode usar um webhook proprio que aceite JSON com `phone`, `message` e `ticket_id`:

```powershell
$env:WHATSAPP_PROVIDER="webhook"
$env:WHATSAPP_WEBHOOK_URL="https://seu-provedor.example.com/send"
```


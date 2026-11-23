# Aurora Voz

O Aurora Voz é meu projeto de assistente pessoal para Windows. Fiz em Python e estou desenvolvendo aos poucos: ele abre em uma janela flutuante, recebe mensagens por voz ou texto e responde em português.

## O que ele faz

- Grava pelo microfone selecionado por até 10 segundos.
- Permite conversar digitando.
- Lê as respostas em voz alta.
- Guarda lembretes no próprio computador.
- Informa a hora e a data.
- Mostra ou esconde a janela com `Ctrl + Alt + A`.

## Para começar

Você vai precisar do Windows, do Python 3.10 ou mais recente, de um microfone e de uma conexão com a internet.

No PowerShell, abra a pasta do projeto e instale as dependências:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

Depois, inicie o Aurora:

```powershell
py main.py
```

Se preferir, também dá para abrir `atalhos/iniciar.bat`.

## Como usar

Escolha o microfone na lista e clique em **Falar agora**. A gravação pode levar até 10 segundos para ser reconhecida. Para escrever, use o campo na parte de baixo da janela e pressione Enter ou clique em **Enviar**.

O Aurora também entende alguns pedidos simples:

- “Lembre que ...” salva uma informação no computador.
- “O que você lembra?” lê as informações salvas.
- “Que horas são?” e “Que dia é hoje?” respondem usando a data e hora do computador.
- “Sair” ou “tchau” encerra a conversa.

As outras mensagens precisam de internet para receber uma resposta do serviço de inteligência artificial e para reconhecer a fala.

## Pastas do projeto

```text
aplicativo/nucleo_aurora/  Código do assistente
atalhos/                  Atalho para iniciar no Windows
identidade/               Marca visual do Aurora
lembrancas/                Lembretes salvos no computador
main.py                    Arquivo que inicia o programa
requirements.txt           Bibliotecas necessárias
```

As lembranças podem conter informações pessoais. O arquivo de memória fica fora do Git para não ser enviado junto com o código.

## Sobre

Projeto criado por **João Victor**. Usei o **Codex** para me auxiliar em algumas partes do código e na organização do projeto.

Última atualização: **23 de novembro de 2026**.

Ainda não escolhi uma licença para o projeto.

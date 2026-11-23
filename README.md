# Como funciona o código do Aurora Voz

## Introdução

O Aurora Voz é um assistente pessoal feito em Python para Windows. Este guia acompanha o caminho que o programa percorre: da abertura da janela à captura da fala, ao processamento das mensagens e à resposta em voz alta. Também mostra onde ficam os lembretes e qual é a função de cada pasta principal.

## Arquivo que inicia o programa

O ponto de entrada é `main.py`. Ele localiza a pasta `aplicativo`, importa a função principal do Aurora e abre a interface.

O código do aplicativo fica em `aplicativo/nucleo_aurora/app.py`. Nele estão a janela, a gravação de áudio, o tratamento das mensagens e a fala das respostas.

## O que acontece ao abrir

1. O programa carrega os lembretes salvos em `lembrancas/memoria.json`.
2. Cria a janela flutuante do Aurora e lista os microfones que o Windows disponibiliza.
3. Exibe a saudação inicial e fica pronto para receber uma mensagem.

A janela pode ser movida pela tela. O atalho `Ctrl + Alt + A` oculta ou mostra o painel.

## Como a conversa funciona

### Mensagem por voz

Ao clicar em **Falar agora**, o Aurora grava até 10 segundos usando o microfone selecionado. O áudio é convertido em texto pelo reconhecimento de fala em português. Em seguida, o programa trata a frase como uma mensagem normal.

### Mensagem por texto

O texto digitado é enviado ao mesmo fluxo de conversa usado pela fala. Assim, comandos como consultar a hora e salvar um lembrete também funcionam pelo campo de texto.

### Comandos locais e respostas de IA

Antes de consultar a IA, o programa verifica se a mensagem corresponde a um comando simples:

- `Lembre que ...` adiciona um fato à memória local.
- `O que você lembra?` lê os fatos guardados.
- Perguntas sobre a hora ou a data são respondidas usando o relógio do computador.
- `Sair`, `encerrar` ou `tchau` encerra a conversa.

As outras mensagens são enviadas ao serviço de IA configurado no aplicativo. O código mantém um histórico curto da conversa para dar contexto às respostas.

## Voz e áudio

O módulo `sounddevice` captura o áudio do microfone. A biblioteca `SpeechRecognition` envia a gravação ao serviço de reconhecimento de fala do Google e recebe o texto reconhecido. Essa etapa precisa de internet.

As respostas são faladas pelo `pyttsx3`, usando a voz SAPI5 disponível no Windows. A captura e as chamadas online rodam em tarefas separadas para a janela continuar respondendo aos cliques.

## Memória local

Os lembretes ficam em `lembrancas/memoria.json`, no formato JSON. As funções `carregar_memoria()` e `salvar_memoria()` leem e atualizam esse arquivo. Ele pode conter dados pessoais e está excluído do Git pelo `.gitignore`.

## Pastas e arquivos

```text
main.py                         Inicia o aplicativo
aplicativo/nucleo_aurora/app.py Interface e lógica do assistente
atalhos/iniciar.bat             Atalho para abrir no Windows
identidade/aurora-mark.svg      Marca visual do projeto
lembrancas/memoria.json         Lembretes locais
requirements.txt                Bibliotecas Python utilizadas
```

## Dependências

- `sounddevice` para gravar pelo microfone.
- `SpeechRecognition` para converter fala em texto.
- `openai` para enviar mensagens ao serviço de IA configurado.
- `pyttsx3` para falar as respostas no Windows.

O projeto foi criado por **João Victor**, com auxílio do **Codex** em algumas partes do código e da organização.

Última atualização: **23 de novembro de 2026**.

import json
import os
import threading
import tkinter as tk
import ctypes
from ctypes import wintypes
from datetime import datetime
from pathlib import Path

import sounddevice as sd
import speech_recognition as sr
from openai import OpenAI
from tkinter import ttk


APP_NAME = "Aurora Voz"
FREQUENCIA = 16000
DURACAO = 10
ROOT_DIR = Path(__file__).resolve().parents[2]
ARQUIVO_MEMORIA = ROOT_DIR / "lembrancas" / "memoria.json"

FUNDO = "#111827"
PAINEL = "#1b2638"
PAINEL_CLARO = "#25344a"
TEXTO = "#f1f5f9"
TEXTO_SUAVE = "#9eacc0"
DESTAQUE = "#4dd6b5"
USUARIO = "#263b50"


def carregar_memoria():
    if not ARQUIVO_MEMORIA.exists():
        return []
    try:
        dados = json.loads(ARQUIVO_MEMORIA.read_text(encoding="utf-8"))
        return dados.get("fatos", [])
    except (json.JSONDecodeError, OSError):
        return []


def salvar_memoria(fatos):
    ARQUIVO_MEMORIA.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO_MEMORIA.write_text(
        json.dumps({"fatos": fatos}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


class AuroraApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        largura, altura = 420, 520
        x = self.root.winfo_screenwidth() - largura - 24
        y = self.root.winfo_screenheight() - altura - 64
        self.root.geometry(f"{largura}x{altura}+{x}+{y}")
        self.root.configure(bg=FUNDO)

        self.memoria = carregar_memoria()
        self.historico = []
        self.reconhecedor = sr.Recognizer()
        self.ocupado = False
        self.microfones = self._listar_microfones()
        self.microfone_por_nome = {nome: indice for nome, indice in self.microfones}
        indice_padrao = sd.default.device[0]
        nome_padrao = next(
            (nome for nome, indice in self.microfones if indice == indice_padrao),
            self.microfones[0][0] if self.microfones else "Nenhum microfone encontrado",
        )
        self.microfone_selecionado = tk.StringVar(value=nome_padrao)

        self._montar_interface()
        self.root.bind("<Escape>", lambda _evento: self.ocultar())
        self.root.protocol("WM_DELETE_WINDOW", self.fechar)
        self._iniciar_atalho_global()
        self._adicionar_mensagem(
            "assistente",
            "Oi! Eu sou o Aurora, assistente de voz criado e programado por João Victor. "
            "Clique em Falar agora ou escreva sua mensagem abaixo.",
        )
        threading.Thread(
            target=self._falar,
            args=(
                "Oi! Eu sou o Aurora, assistente de voz criado e programado por João Victor. "
                "Clique em Falar agora ou escreva sua mensagem abaixo.",
            ),
            daemon=True,
        ).start()

    def _montar_interface(self):
        topo = tk.Frame(self.root, bg=PAINEL, padx=12, pady=10)
        topo.pack(fill="x")
        topo.bind("<ButtonPress-1>", self._iniciar_arrasto)
        topo.bind("<B1-Motion>", self._arrastar)

        marca = tk.Frame(topo, bg=PAINEL)
        marca.pack(side="left")
        marca.bind("<ButtonPress-1>", self._iniciar_arrasto)
        marca.bind("<B1-Motion>", self._arrastar)
        icone = tk.Label(
            marca, text="A", font=("Segoe UI", 12, "bold"),
            fg="#09231f", bg=DESTAQUE, width=2, height=1,
        )
        icone.pack(side="left", padx=(0, 8))
        icone.bind("<ButtonPress-1>", self._iniciar_arrasto)
        icone.bind("<B1-Motion>", self._arrastar)
        textos = tk.Frame(marca, bg=PAINEL)
        textos.pack(side="left")
        textos.bind("<ButtonPress-1>", self._iniciar_arrasto)
        textos.bind("<B1-Motion>", self._arrastar)
        titulo = tk.Label(
            textos, text=APP_NAME, font=("Segoe UI", 11, "bold"),
            fg=TEXTO, bg=PAINEL,
        )
        titulo.pack(anchor="w")
        titulo.bind("<ButtonPress-1>", self._iniciar_arrasto)
        titulo.bind("<B1-Motion>", self._arrastar)
        subtitulo = tk.Label(
            textos, text="PRONTO QUANDO VOCÊ ESTIVER", font=("Segoe UI", 7, "bold"),
            fg=TEXTO_SUAVE, bg=PAINEL,
        )
        subtitulo.pack(anchor="w", pady=(1, 0))
        subtitulo.bind("<ButtonPress-1>", self._iniciar_arrasto)
        subtitulo.bind("<B1-Motion>", self._arrastar)

        controles = tk.Frame(topo, bg=PAINEL)
        controles.pack(side="right")
        self._botao_topo(controles, "—", self.ocultar).pack(side="left", padx=(0, 4))
        self._botao_topo(controles, "×", self.fechar).pack(side="left")

        self.estado = tk.StringVar(value="Pronto para conversar")
        tk.Label(
            self.root, textvariable=self.estado, font=("Segoe UI", 9),
            fg=TEXTO_SUAVE, bg=FUNDO, anchor="w", padx=16, pady=8,
        ).pack(fill="x")

        seletor = tk.Frame(self.root, bg=FUNDO, padx=16, pady=0)
        seletor.pack(fill="x", pady=(0, 8))
        tk.Label(
            seletor, text="Microfone", font=("Segoe UI", 8, "bold"),
            fg=TEXTO_SUAVE, bg=FUNDO,
        ).pack(side="left", padx=(0, 8))
        self.lista_microfones = ttk.Combobox(
            seletor, textvariable=self.microfone_selecionado,
            values=[nome for nome, _indice in self.microfones],
            state="readonly" if self.microfones else "disabled",
            width=21,
        )
        self.lista_microfones.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.lista_microfones.bind("<<ComboboxSelected>>", self._microfone_alterado)
        self.botao_microfone = tk.Button(
            seletor, text="Falar agora", command=self.iniciar_gravacao,
            bg=DESTAQUE, fg="#09231f", activebackground="#72e6c9",
            activeforeground="#09231f", relief="flat", bd=0,
            font=("Segoe UI", 9, "bold"), padx=10, pady=6,
            cursor="hand2", state="normal" if self.microfones else "disabled",
        )
        self.botao_microfone.pack(side="right")

        conversa = tk.Frame(self.root, bg=FUNDO, padx=12, pady=4)
        conversa.pack(fill="both", expand=True)
        self.transcricao = tk.Text(
            conversa, wrap="word", state="disabled", relief="flat",
            bg=FUNDO, fg=TEXTO, font=("Segoe UI", 10),
            padx=4, pady=4, spacing1=4, spacing3=10,
            insertbackground=TEXTO, selectbackground=PAINEL_CLARO,
        )
        barra = tk.Scrollbar(conversa, command=self.transcricao.yview)
        self.transcricao.configure(yscrollcommand=barra.set)
        self.transcricao.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.transcricao.tag_configure("nome_assistente", foreground=DESTAQUE,
                                       font=("Segoe UI", 9, "bold"))
        self.transcricao.tag_configure("nome_usuario", foreground="#9bc7ff",
                                       font=("Segoe UI", 9, "bold"))
        self.transcricao.tag_configure("fala_assistente", foreground=TEXTO,
                                       lmargin1=12, lmargin2=12, rmargin=34,
                                       spacing1=4, spacing3=12)
        self.transcricao.tag_configure("fala_usuario", foreground=TEXTO,
                                       lmargin1=38, lmargin2=38, rmargin=8,
                                       spacing1=4, spacing3=12)

        rodape = tk.Frame(self.root, bg=PAINEL, padx=12, pady=12)
        rodape.pack(fill="x")
        linha = tk.Frame(rodape, bg=PAINEL_CLARO, padx=9, pady=7)
        linha.pack(fill="x")
        self.entrada = tk.Entry(
            linha, relief="flat", bg=PAINEL_CLARO, fg=TEXTO,
            insertbackground=TEXTO, font=("Segoe UI", 10),
        )
        self.entrada.pack(side="left", fill="x", expand=True, padx=(3, 8))
        self.entrada.insert(0, "Escreva uma mensagem...")
        self.entrada.config(fg=TEXTO_SUAVE)
        self.entrada.bind("<FocusIn>", self._limpar_placeholder)
        self.entrada.bind("<Return>", lambda _evento: self.enviar_texto())

        self.botao_enviar = tk.Button(
            linha, text="Enviar", command=self.enviar_texto,
            bg=PAINEL_CLARO, fg=TEXTO, activebackground="#31445e",
            activeforeground=TEXTO, relief="flat", bd=0,
            font=("Segoe UI", 9, "bold"), padx=12, pady=7, cursor="hand2",
        )
        self.botao_enviar.pack(side="right")

        tk.Label(
            rodape, text=f"CTRL + ALT + A para mostrar ou ocultar · Áudio até {DURACAO}s",
            font=("Segoe UI", 8), fg=TEXTO_SUAVE, bg=FUNDO,
        ).pack(anchor="center", pady=(9, 0))

    @staticmethod
    def _botao_topo(pai, rotulo, comando):
        return tk.Button(
            pai, text=rotulo, command=comando, bg=PAINEL_CLARO, fg=TEXTO,
            activebackground="#31445e", activeforeground=TEXTO,
            relief="flat", bd=0, font=("Segoe UI", 10, "bold"),
            width=3, cursor="hand2",
        )

    @staticmethod
    def _listar_microfones():
        try:
            return [
                (f"{indice} · {dispositivo['name']}", indice)
                for indice, dispositivo in enumerate(sd.query_devices())
                if dispositivo["max_input_channels"] > 0
            ]
        except Exception:
            return []

    def _microfone_alterado(self, _evento=None):
        self.estado.set(f"Microfone selecionado: {self.microfone_selecionado.get()}")

    def _iniciar_arrasto(self, evento):
        self._arrasto_x = evento.x_root - self.root.winfo_x()
        self._arrasto_y = evento.y_root - self.root.winfo_y()

    def _arrastar(self, evento):
        self.root.geometry(f"+{evento.x_root - self._arrasto_x}+{evento.y_root - self._arrasto_y}")

    def ocultar(self):
        self.root.withdraw()

    def mostrar(self):
        self.root.deiconify()
        self.root.attributes("-topmost", True)
        self.root.lift()

    def alternar_visibilidade(self):
        if self.root.state() == "withdrawn":
            self.mostrar()
        else:
            self.ocultar()

    def fechar(self):
        self.root.destroy()

    def _iniciar_atalho_global(self):
        def escutar_atalho():
            try:
                user32 = ctypes.windll.user32
                MOD_ALT = 0x0001
                MOD_CONTROL = 0x0002
                VK_A = 0x41
                WM_HOTKEY = 0x0312
                if not user32.RegisterHotKey(None, 1, MOD_ALT | MOD_CONTROL, VK_A):
                    self.root.after(0, self.estado.set,
                                    "Atalho Ctrl+Alt+A indisponível neste Windows")
                    return
                mensagem = wintypes.MSG()
                while user32.GetMessageW(ctypes.byref(mensagem), None, 0, 0) > 0:
                    if mensagem.message == WM_HOTKEY and mensagem.wParam == 1:
                        self.root.after(0, self.alternar_visibilidade)
                user32.UnregisterHotKey(None, 1)
            except (AttributeError, OSError):
                self.root.after(0, self.estado.set, "Atalho global disponível apenas no Windows")

        threading.Thread(target=escutar_atalho, daemon=True).start()

    def _limpar_placeholder(self, _evento=None):
        if self.entrada.get() == "Escreva uma mensagem...":
            self.entrada.delete(0, "end")
            self.entrada.config(fg=TEXTO)

    def _adicionar_mensagem(self, autor, mensagem):
        self.transcricao.configure(state="normal")
        if autor == "usuario":
            self.transcricao.insert("end", "Você\n", "nome_usuario")
            self.transcricao.insert("end", f"{mensagem}\n\n", "fala_usuario")
        else:
            self.transcricao.insert("end", "Aurora\n", "nome_assistente")
            self.transcricao.insert("end", f"{mensagem}\n\n", "fala_assistente")
        self.transcricao.configure(state="disabled")
        self.transcricao.see("end")

    def _definir_ocupado(self, ocupado, estado=None):
        self.ocupado = ocupado
        self.botao_microfone.configure(state="disabled" if ocupado else "normal")
        self.botao_enviar.configure(state="disabled" if ocupado else "normal")
        if estado:
            self.estado.set(estado)
        elif not ocupado:
            self.estado.set("Pronto para conversar")

    def enviar_texto(self):
        texto = self.entrada.get().strip()
        if not texto or texto == "Escreva uma mensagem..." or self.ocupado:
            return
        self.entrada.delete(0, "end")
        self.entrada.config(fg=TEXTO)
        self._adicionar_mensagem("usuario", texto)
        self._processar_em_thread(texto)

    def iniciar_gravacao(self):
        if self.ocupado:
            return
        self._definir_ocupado(True, f"Gravando... fale agora (até {DURACAO}s)")
        threading.Thread(target=self._gravar_e_transcrever, daemon=True).start()

    def _gravar_e_transcrever(self):
        try:
            dispositivo = self.microfone_por_nome.get(self.microfone_selecionado.get())
            if dispositivo is None:
                raise RuntimeError("Nenhum microfone de entrada está disponível.")

            info = sd.query_devices(dispositivo, "input")
            taxas = [FREQUENCIA, int(info["default_samplerate"]), 44100, 48000]
            taxa_amostragem = None
            for taxa in dict.fromkeys(taxas):
                try:
                    sd.check_input_settings(
                        device=dispositivo, channels=1,
                        dtype="int16", samplerate=taxa,
                    )
                    taxa_amostragem = taxa
                    break
                except sd.PortAudioError:
                    continue
            if taxa_amostragem is None:
                raise RuntimeError(
                    f"O microfone {info['name']} não aceita os formatos de áudio disponíveis."
                )

            self.root.after(0, self.estado.set,
                            f"Gravando em {info['name']}... fale agora por até {DURACAO}s")
            amostra = sd.rec(
                int(DURACAO * taxa_amostragem), samplerate=taxa_amostragem,
                channels=1, dtype="int16", device=dispositivo,
            )
            sd.wait()
            self.root.after(0, self.estado.set, "Áudio capturado; reconhecendo sua fala...")
            audio = sr.AudioData(amostra.tobytes(), taxa_amostragem, 2)
            texto = self.reconhecedor.recognize_google(audio, language="pt-BR")
            self.root.after(0, self._fala_reconhecida, texto)
        except sr.UnknownValueError:
            self.root.after(0, self._mostrar_resposta, "Não consegui entender. Pode tentar de novo?")
        except sr.RequestError as erro:
            self.root.after(0, self._mostrar_resposta,
                            f"Não consegui acessar o reconhecimento de voz: {erro}")
        except Exception as erro:
            self.root.after(0, self._mostrar_resposta, f"Não consegui gravar o áudio: {erro}")

    def _fala_reconhecida(self, texto):
        self._adicionar_mensagem("usuario", texto)
        self._processar_em_thread(texto)

    def _processar_em_thread(self, texto):
        self._definir_ocupado(True, "Preparando uma resposta...")
        threading.Thread(
            target=self._processar_mensagem, args=(texto,), daemon=True
        ).start()

    def _processar_mensagem(self, texto):
        try:
            pergunta = texto.casefold().strip()
            if pergunta in ("encerrar", "sair", "tchau"):
                resposta = "Até logo! Pode fechar a janela quando quiser."
            elif pergunta.startswith("lembre que"):
                fato = texto[len("lembre que"):].strip(" .,:;")
                if not fato:
                    resposta = "O que você quer que eu lembre?"
                elif fato in self.memoria:
                    resposta = "Eu já tenho isso na memória."
                else:
                    self.memoria.append(fato)
                    salvar_memoria(self.memoria)
                    resposta = f"Pronto. Vou lembrar que {fato}."
            elif "o que você lembra" in pergunta or "o que voce lembra" in pergunta:
                resposta = ("Eu lembro: " + "; ".join(self.memoria)
                            if self.memoria else "Ainda não tenho nenhuma memória salva.")
            elif "que horas" in pergunta or pergunta == "horas":
                resposta = f"Agora são {datetime.now():%H:%M}."
            elif "que dia" in pergunta or "qual é a data" in pergunta:
                resposta = f"Hoje é {datetime.now():%d/%m/%Y}."
            else:
                chave = os.environ.get("GROQ_API_KEY")
                if not chave:
                    raise RuntimeError(
                        "A variável GROQ_API_KEY não está configurada. "
                        "Defina a chave no PowerShell e abra o programa novamente."
                    )
                self.historico.append(f"Usuário: {texto}")
                cliente = OpenAI(
                    api_key=chave,
                    base_url="https://api.groq.com/openai/v1",
                )
                resposta_api = cliente.responses.create(
                    model="openai/gpt-oss-20b",
                    instructions=(
                        "Você é o Aurora, um assistente de voz criado e programado por João Victor. "
                        "Responda em português do Brasil e em no máximo duas frases. "
                        "Se perguntarem quem criou ou programou você, responda que foi João Victor. "
                        "Não diga que o Aurora foi criado ou programado pela OpenAI. "
                        "Use as memórias apenas quando forem relevantes.\n\n"
                        "Memórias permanentes:\n"
                        + ("\n".join(f"- {fato}" for fato in self.memoria)
                           or "- Nenhuma memória salva.")
                    ),
                    input=("Conversa recente:\n" + "\n".join(self.historico[-6:])
                           + "\n\nResponda à última mensagem do usuário."),
                )
                resposta = resposta_api.output_text.strip()
                self.historico.append(f"Aurora: {resposta}")
            self.root.after(0, self._mostrar_resposta, resposta)
        except Exception as erro:
            self.root.after(0, self._mostrar_resposta, f"Ocorreu um erro: {erro}")

    def _mostrar_resposta(self, mensagem):
        self._adicionar_mensagem("assistente", mensagem)
        self.estado.set("Resposta pronta")
        self._definir_ocupado(False)
        threading.Thread(target=self._falar, args=(mensagem,), daemon=True).start()

    @staticmethod
    def _falar(mensagem):
        try:
            import pyttsx3

            voz = pyttsx3.init("sapi5")
            voz.setProperty("volume", 1.0)
            voz.setProperty("rate", 180)
            voz.say(mensagem)
            voz.runAndWait()
            voz.stop()
        except Exception:
            pass


def main():
    root = tk.Tk()
    AuroraApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

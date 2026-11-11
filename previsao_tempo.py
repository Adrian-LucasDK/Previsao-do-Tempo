
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
from datetime import datetime

# ==========================================
# CONFIGURAÇÕES
# ==========================================

COR_FUNDO = "#20232A"
COR_CARD = "#2D323C"
COR_TEXTO = "#FFFFFF"
COR_DESTAQUE = "#61AFEF"

URL_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"
URL_PREVISAO = "https://api.open-meteo.com/v1/forecast"

# Tradução dos códigos de condição do tempo (WMO)
CONDICOES = {
    0: "Céu limpo",
    1: "Predominantemente limpo",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Neblina",
    48: "Neblina com geada",
    51: "Garoa fraca",
    53: "Garoa moderada",
    55: "Garoa intensa",
    56: "Garoa congelante fraca",
    57: "Garoa congelante intensa",
    61: "Chuva fraca",
    63: "Chuva moderada",
    65: "Chuva intensa",
    66: "Chuva congelante fraca",
    67: "Chuva congelante intensa",
    71: "Neve fraca",
    73: "Neve moderada",
    75: "Neve intensa",
    77: "Granizo de neve",
    80: "Pancadas de chuva fracas",
    81: "Pancadas de chuva moderadas",
    82: "Pancadas de chuva intensas",
    85: "Pancadas de neve fracas",
    86: "Pancadas de neve intensas",
    95: "Tempestade",
    96: "Tempestade com granizo",
    99: "Tempestade forte com granizo"
}

DIAS_SEMANA = [
    "Segunda-feira", "Terça-feira", "Quarta-feira",
    "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"
]


# ==========================================
# FUNÇÃO PARA BUSCAR A CIDADE
# ==========================================

def buscar_cidade(nome_cidade):
    parametros = {
        "name": nome_cidade,
        "count": 1,
        "language": "pt",
        "format": "json"
    }

    resposta = requests.get(
        URL_GEOCODING,
        params=parametros,
        timeout=15
    )

    resposta.raise_for_status()
    dados = resposta.json()

    if not dados.get("results"):
        raise ValueError("Cidade não encontrada.")

    return dados["results"][0]


# ==========================================
# FUNÇÃO PARA BUSCAR A PREVISÃO
# ==========================================

def buscar_previsao(latitude, longitude):
    parametros = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "weather_code,"
            "wind_speed_10m"
        ),
        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max"
        ),
        "forecast_days": 7,
        "timezone": "auto"
    }

    resposta = requests.get(
        URL_PREVISAO,
        params=parametros,
        timeout=15
    )

    resposta.raise_for_status()
    return resposta.json()


# ==========================================
# ATUALIZAR A INTERFACE
# ==========================================

def atualizar_interface(cidade, previsao):

    atual = previsao["current"]
    diaria = previsao["daily"]

    # Informações da cidade
    nome = cidade["name"]
    pais = cidade.get("country", "")
    estado = cidade.get("admin1", "")

    local = nome

    if estado:
        local += f", {estado}"

    if pais:
        local += f" - {pais}"

    label_cidade.config(text=local)

    # Condição atual
    codigo = atual["weather_code"]
    condicao = CONDICOES.get(codigo, "Condição desconhecida")

    label_condicao.config(text=condicao)

    # Temperatura
    temperatura = atual["temperature_2m"]
    label_temperatura.config(
        text=f"{temperatura:.1f} °C"
    )

    # Outras informações
    label_sensacao.config(
        text=f"Sensação térmica: {atual['apparent_temperature']} °C"
    )

    label_umidade.config(
        text=f"Umidade: {atual['relative_humidity_2m']}%"
    )

    label_vento.config(
        text=f"Vento: {atual['wind_speed_10m']} km/h"
    )

    # Limpar previsão anterior
    for widget in frame_dias.winfo_children():
        widget.destroy()

    # Mostrar previsão dos próximos 7 dias
    for i in range(len(diaria["time"])):

        data = datetime.strptime(
            diaria["time"][i], "%Y-%m-%d"
        )

        dia = DIAS_SEMANA[data.weekday()]

        codigo_dia = diaria["weather_code"][i]
        descricao = CONDICOES.get(
            codigo_dia, "Condição desconhecida"
        )

        maxima = diaria["temperature_2m_max"][i]
        minima = diaria["temperature_2m_min"][i]
        chuva = diaria["precipitation_probability_max"][i]

        texto = (
            f"{dia} ({data.strftime('%d/%m')})\n"
            f"{descricao}\n"
            f"Máxima: {maxima} °C   |   "
            f"Mínima: {minima} °C   |   "
            f"Chuva: {chuva}%"
        )

        item = tk.Label(
            frame_dias,
            text=texto,
            bg=COR_CARD,
            fg=COR_TEXTO,
            font=("Arial", 10),
            justify="left",
            anchor="w",
            padx=12,
            pady=10
        )

        item.pack(fill="x", pady=4)


# ==========================================
# PESQUISA EM SEGUNDO PLANO
# ==========================================

def pesquisar_tempo():

    nome_cidade = entrada_cidade.get().strip()

    if not nome_cidade:
        messagebox.showwarning(
            "Atenção",
            "Digite o nome de uma cidade."
        )
        return

    botao_buscar.config(state="disabled")
    label_status.config(text="Consultando previsão do tempo...")

    def executar_busca():

        try:
            cidade = buscar_cidade(nome_cidade)

            previsao = buscar_previsao(
                cidade["latitude"],
                cidade["longitude"]
            )

            janela.after(
                0,
                lambda: finalizar_busca(cidade, previsao, None)
            )

        except Exception as erro:

            janela.after(
                0,
                lambda: finalizar_busca(None, None, str(erro))
            )

    threading.Thread(
        target=executar_busca,
        daemon=True
    ).start()


def finalizar_busca(cidade, previsao, erro):

    botao_buscar.config(state="normal")

    if erro:
        label_status.config(text="Não foi possível consultar os dados.")
        messagebox.showerror(
            "Erro",
            f"Ocorreu um problema:\n{erro}"
        )
        return

    atualizar_interface(cidade, previsao)
    label_status.config(text="Previsão atualizada com sucesso!")


# ==========================================
# INTERFACE GRÁFICA
# ==========================================

janela = tk.Tk()
janela.title("Previsão do Tempo")
janela.geometry("650x750")
janela.minsize(550, 600)
janela.configure(bg=COR_FUNDO)

# Título
titulo = tk.Label(
    janela,
    text="PREVISÃO DO TEMPO",
    font=("Arial", 20, "bold"),
    bg=COR_FUNDO,
    fg=COR_TEXTO
)
titulo.pack(pady=(20, 5))

subtitulo = tk.Label(
    janela,
    text="Consulte o clima de qualquer cidade",
    font=("Arial", 10),
    bg=COR_FUNDO,
    fg="#AAAAAA"
)
subtitulo.pack(pady=(0, 20))

# Área de pesquisa
frame_pesquisa = tk.Frame(
    janela,
    bg=COR_FUNDO
)
frame_pesquisa.pack(padx=25, fill="x")

entrada_cidade = tk.Entry(
    frame_pesquisa,
    font=("Arial", 12),
    bg=COR_CARD,
    fg=COR_TEXTO,
    insertbackground=COR_TEXTO,
    relief="flat"
)
entrada_cidade.pack(
    side="left",
    fill="x",
    expand=True,
    ipady=10,
    padx=(0, 10)
)

entrada_cidade.insert(0, "Tefé")

botao_buscar = tk.Button(
    frame_pesquisa,
    text="Buscar",
    font=("Arial", 11, "bold"),
    bg=COR_DESTAQUE,
    fg="#FFFFFF",
    activebackground="#398CCB",
    relief="flat",
    cursor="hand2",
    command=pesquisar_tempo
)
botao_buscar.pack(side="right", ipadx=15, ipady=7)

# Status da pesquisa
label_status = tk.Label(
    janela,
    text="Digite uma cidade para consultar.",
    bg=COR_FUNDO,
    fg="#AAAAAA",
    font=("Arial", 9)
)
label_status.pack(pady=10)

# Cartão com informações atuais
frame_atual = tk.Frame(
    janela,
    bg=COR_CARD,
    padx=20,
    pady=20
)
frame_atual.pack(
    fill="x",
    padx=25,
    pady=10
)

label_cidade = tk.Label(
    frame_atual,
    text="Cidade",
    bg=COR_CARD,
    fg=COR_TEXTO,
    font=("Arial", 15, "bold")
)
label_cidade.pack()

label_condicao = tk.Label(
    frame_atual,
    text="Condição do tempo",
    bg=COR_CARD,
    fg="#AAAAAA",
    font=("Arial", 11)
)
label_condicao.pack(pady=5)

label_temperatura = tk.Label(
    frame_atual,
    text="-- °C",
    bg=COR_CARD,
    fg=COR_DESTAQUE,
    font=("Arial", 38, "bold")
)
label_temperatura.pack(pady=5)

label_sensacao = tk.Label(
    frame_atual,
    text="Sensação térmica: -- °C",
    bg=COR_CARD,
    fg=COR_TEXTO,
    font=("Arial", 10)
)
label_sensacao.pack(pady=3)

label_umidade = tk.Label(
    frame_atual,
    text="Umidade: --%",
    bg=COR_CARD,
    fg=COR_TEXTO,
    font=("Arial", 10)
)
label_umidade.pack(pady=3)

label_vento = tk.Label(
    frame_atual,
    text="Vento: -- km/h",
    bg=COR_CARD,
    fg=COR_TEXTO,
    font=("Arial", 10)
)
label_vento.pack(pady=3)

# Título da previsão semanal
titulo_dias = tk.Label(
    janela,
    text="PREVISÃO PARA OS PRÓXIMOS 7 DIAS",
    font=("Arial", 12, "bold"),
    bg=COR_FUNDO,
    fg=COR_TEXTO
)
titulo_dias.pack(pady=(15, 10))

# Área rolável da previsão
container = tk.Frame(janela, bg=COR_FUNDO)
container.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=(0, 15)
)

canvas = tk.Canvas(
    container,
    bg=COR_FUNDO,
    highlightthickness=0
)

scrollbar = ttk.Scrollbar(
    container,
    orient="vertical",
    command=canvas.yview
)

frame_dias = tk.Frame(
    canvas,
    bg=COR_FUNDO
)

frame_dias.bind(
    "<Configure>",
    lambda evento: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window(
    (0, 0),
    window=frame_dias,
    anchor="nw",
    width=580
)

canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Permitir pesquisa apertando Enter
entrada_cidade.bind(
    "<Return>",
    lambda evento: pesquisar_tempo()
)

# Iniciar o programa
janela.mainloop()

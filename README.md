# 🌤️ Aplicativo de Previsão do Tempo

Aplicativo desenvolvido em Python com interface gráfica utilizando Tkinter, que consome uma API de previsão meteorológica para apresentar informações climáticas de diferentes cidades.

## 🚀 Funcionalidades

- Pesquisa de cidades pelo nome.
- Consulta da temperatura atual.
- Exibição da sensação térmica.
- Exibição da umidade do ar.
- Exibição da velocidade do vento.
- Identificação das condições climáticas.
- Previsão do tempo para os próximos 7 dias.
- Exibição das temperaturas máximas e mínimas.
- Probabilidade de precipitação.
- Interface gráfica com área de previsão rolável.
- Tratamento de erros de conexão e cidades não encontradas.

## 🛠️ Tecnologias utilizadas

- Python
- Tkinter
- Requests
- Threading
- Datetime
- Open-Meteo API

## 📋 Requisitos

- Python 3 instalado.
- Conexão com a internet.

Instale a biblioteca necessária:

```bash
pip install requests
```

## ▶️ Como executar

1. Clone este repositório:

```bash
git clone URL_DO_REPOSITORIO
```

2. Entre na pasta do projeto:

```bash
cd previsao-do-tempo
```

3. Instale as dependências:

```bash
pip install requests
```

4. Execute o programa:

```bash
python previsao_tempo.py
```

## 🌐 APIs utilizadas

**Open-Meteo Geocoding API:** utilizada para localizar cidades e obter suas coordenadas geográficas.

**Open-Meteo Weather API:** utilizada para consultar as condições climáticas atuais e a previsão para os próximos dias.

Documentação: [https://open-meteo.com/en/docs](https://open-meteo.com/en/docs)

## 📚 Objetivo

Projeto desenvolvido para praticar consumo de APIs REST, requisições HTTP, processamento de dados JSON, utilização de threads, manipulação de datas e desenvolvimento de interfaces gráficas com Python.

## 👨‍💻 Autor

Desenvolvido por Adrian Lucas.
# Formula1DW: Pit-Wall Dashboard

Data warehouse e dashboard da temporada de F1 2025: pipeline ETL, banco em
estrela no SQL Server, e um painel Streamlit com identidade visual de telão
de muro de boxes.

![Home](docs/screenshots/home.jpg)

## O que é

Extrai dados reais da F1 (resultados, classificação, tempos de volta, pit
stops, clima e telemetria) via **Jolpica-F1** (sucessor do Ergast API) e
**FastF1**. Carrega tudo num data warehouse em estrela no SQL Server e
expõe num dashboard Streamlit com 5 páginas, em PT e EN.

```
Jolpica-F1 / FastF1  →  ETL (Python)  →  SQL Server (star schema)
                                              │
                                       mart views (SQL)
                                              │
                                 snapshot .sqlite (scripts/export_sqlite.py)
                                              │
                                    Streamlit dashboard
```

O dashboard lê de um snapshot `.sqlite` já incluído no repo. Roda direto,
sem precisar de SQL Server no ar.

## Como foi construído

O projeto saiu em fases, cada uma resolvendo um problema específico antes de
passar pra próxima.

#### Banco em camadas

`raw` espelha o formato bruto da Jolpica-F1/FastF1 sem tipagem forte. `stg`
tipa e limpa, pronto pra MERGE. `dw` é o modelo em estrela de verdade:
dimensões e fatos com chave substituta. `mart` são views de consumo em cima
do `dw`, pra quem só quer ler não precisar entender grain de fato nem chave
substituta. Cada schema tem seu próprio script em `database/`, e as
procedures de carga usam MERGE, então rodar de novo não duplica linha.

#### Pipeline incremental

`etl/run.py` decide o que falta carregar consultando direto `dw.DimRace` e
`dw.FactResults`: se a corrida já está lá, pula. Não existe tabela de
checkpoint própria. A exceção é a última corrida carregada, que ele sempre
reprocessa, porque a FIA aplica punição pós-corrida e o resultado pode
mudar depois do primeiro carregamento. Falha de extração e falha de carga
saem com código de erro diferente, pra dar pra saber onde parou sem abrir o
log inteiro.

#### Telemetria sob demanda

`dw.FactTelemetry` sozinho, carregado pra todo mundo, é volume grande
demais pra fazer sentido sem pedir. Fica fora do pipeline principal:
`python -m etl.telemetry --season S --round R --driver D` carrega só aquele
piloto naquela corrida.

#### Geometria de pista

O problema aqui era achar a coordenada X/Y exata onde um setor de
cronometragem termina, e nenhum dado da FastF1 responde isso direto.
Detalhes na seção própria mais abaixo.

#### Validação manual no fim

Depois de tudo montado, rodei os números do dashboard contra o banco
direto, um por um. Achei dois bugs reais assim. A soma de pontos por
construtor tratava piloto como grão em vez de equipe, e dois pilotos do
mesmo time geravam duas somas acumuladas diferentes pro mesmo round. A
telemetria de um carro que abandona continua gravando parado no box,
empilhando centenas de leituras na mesma coordenada. Os dois estão
corrigidos no código atual.

## Páginas do dashboard

### Home

Visão geral da temporada: líder do campeonato (piloto e construtor), mais
vitórias, mais poles, volta mais rápida, e os top 5 de pontos em piloto e
construtor.

Líder do campeonato é quem tem mais pontos acumulados na rodada mais
recente já disputada. Mais vitórias e mais poles contam 1º lugar na corrida
e na classificação de largada, somando a temporada inteira. Volta mais
rápida é a menor volta cronometrada da temporada, entre todos os pilotos e
todas as corridas.

### Standings

Evolução de pontos rodada a rodada em gráfico de linha, para todos os
pilotos e construtores, com líder atual e diferença para o 2º lugar.

Os pontos acumulados (`RunningPoints`) são uma soma corrida por corrida.
Para construtores, os pontos dos dois pilotos são somados por rodada antes
de acumular: somar direto sobre a granularidade piloto/corrida gera duas
linhas empatadas por rodada e quebra a soma acumulada quando há empate de
pontos entre pilotos do mesmo time.

### Race

Resultado de uma corrida específica: grid de largada, posição final,
pontos, pit stops e clima da sessão. Pontos seguem a tabela oficial da FIA
(25-18-15-12-10-8-6-4-2-1 para o top 10, mais 1 ponto extra para quem faz
a volta mais rápida terminando entre os 10 primeiros).

### Laps & Telemetry

Tempos de volta por composto de pneu, melhor volta, volta média, e
telemetria detalhada (velocidade, marcha, acelerador) de uma volta
escolhida.

Melhor volta e volta média são o menor tempo e a média dos tempos de volta
do piloto naquela corrida. A telemetria vem de amostras de velocidade,
marcha e acelerador ao longo da distância percorrida na volta, direto do
canal de telemetria do carro captado pela FastF1, o mesmo dado usado nas
transmissões oficiais.

![Laps & Telemetry](docs/screenshots/laps-telemetry.jpg)

### Track Map

Geometria da pista colorida pelo piloto mais rápido em cada um dos 3
setores oficiais, mais um ranking de melhor volta da corrida selecionada.

Setor 1, 2 e 3 são os setores oficiais de cronometragem da FIA (divisões
fixas da pista, não curvas específicas). Cada um tem um tempo parcial
próprio, e o piloto mais rápido em cada setor pode não ser o mesmo que
venceu a corrida. Essa página é a mais trabalhosa do projeto; a seção
abaixo explica como ela foi construída.

![Track Map](docs/screenshots/track-map.jpg)

## Como o Track Map foi feito

A FastF1 dá dois tipos de dado que não se conectam direto: o tempo de
cada setor por volta (`Sector1Millis`, `Sector2Millis`, `Sector3Millis`,
que são durações) e a telemetria do carro (posição X/Y a cada distância
percorrida). Nenhum dos dois diz em que ponto exato da pista um setor
termina e o outro começa.

A solução, em `etl/track_map.py`:

1. Escolhe a volta mais rápida da corrida como volta de referência para a
   geometria, não importa de qual piloto.
2. Soma os tempos de setor dessa volta para achar os instantes de
   fronteira: o fim do setor 1 é `Sector1Millis`; o fim do setor 2 é
   `Sector1Millis + Sector2Millis`.
3. Na telemetria dessa volta, ordenada pelo tempo decorrido desde o
   início da volta, encontra as duas amostras que cercam cada instante de
   fronteira e interpola linearmente `Distance`, `X` e `Y` entre elas. Não
   usa a amostra mais próxima; calcula a fração exata entre as duas
   amostras vizinhas.
4. Com as fronteiras convertidas em distância percorrida, marca cada
   ponto de telemetria da volta como setor 1, 2 ou 3.

A parte que fica menos óbvia lendo só o mapa: o desenho da pista vem da
forma de uma única volta de referência, mas a cor de cada trecho é
independente disso. Cada setor é colorido pelo piloto mais rápido
*naquele setor específico* da corrida inteira, que pode ser um piloto
diferente do dono da volta de referência.

Telemetria não é carregada em massa (o volume por corrida é grande demais
para carregar de todo mundo); ela entra sob demanda por piloto e corrida
via `etl/telemetry.py`. Se a volta de referência escolhida não tiver
telemetria carregada ainda, `etl/track_map.py` para com um erro apontando
o comando exato a rodar antes, em vez de travar em silêncio ou carregar
sozinho.

## Stack

- Extração: `fastf1` (Ergast/Jolpica + telemetria FastF1)
- Banco: SQL Server, star schema (`dw.Dim*` / `dw.Fact*`) e mart views
- ETL: Python, `pandas` com `SQLAlchemy`/`pyodbc`, checkpoint idempotente
- Dashboard: `streamlit` e `plotly`

## Como rodar o dashboard

```bash
pip install -r requirements.txt
streamlit run dashboard/Home.py
```

Abre em `http://localhost:8501`. Usa o snapshot `dashboard/data/formula1dw.sqlite`
já commitado, então não precisa de banco rodando.

## Rodar o pipeline ETL completo

Requer SQL Server local (`Formula1DW`, ver `database/`) e ODBC Driver 18.

```bash
pip install -r requirements.txt
python -m etl.run                          # checkpoint mode
python -m etl.telemetry --season 2025 --round 1 --driver VER   # telemetria sob demanda
python -m scripts.export_sqlite            # regenera o snapshot do dashboard
```

Detalhes em `etl/README.md` e `database/README.md`.

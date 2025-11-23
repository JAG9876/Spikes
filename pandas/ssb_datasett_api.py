#!/usr/bin/env python
# coding: utf-8

# # Eksempel 1 - hente CSV fra SSB til pandas
# ## Enkel figur basert på et veldig lite datasett fra SSBs API:ferdige datasett
# ### Henter [sesongjustert detaljomsetningsindeks](https://data.ssb.no/api/v0/dataset/1066) som CSV 


# Importerer Python pandas for å kunne lage dataframe
import pandas as pd
import matplotlib.pyplot as plt

# pd.read_csv() henter innholdet fra API-et og legger det i data. 
# De norske datasettene her er semikolonseparert med komma som desimaltegn.
# CSV er ikke UTF-8, så vi må angi parameter encoding for å få æøå riktig. 

data = pd.read_csv("https://data.ssb.no/api/v0/dataset/1066.csv?lang=no", sep=';', decimal=',', encoding = "ISO-8859-1", )


# Sjekker at datatypen Pandas dataframe
type(data)

# Shape gir antall rader (13) og kolonner (4)
data.shape

# Toppen av datasettet
data.head()

# Endrer til datoformat ved først å erstatte M med -
data['måned']= pd.to_datetime(data['måned'].str.replace('M', '-'))

data.index = data['måned']

# Legger informasjon om innholdet i dataframe
data.info()

# Lage et linjediagram der vi angir x og y aksen med plot i pandas
data.plot(x='måned', y='07129: Varehandelsindeksen, etter næring, måned og statistikkvariabel', figsize=(6, 12), color ='g')

# Alternativ: Trekker ut index (måned) og verdier til en egfen dataframe
data_serie = data['07129: Varehandelsindeksen, etter næring, måned og statistikkvariabel']

# plot med standardverdier
data_serie.plot()

plt.show()

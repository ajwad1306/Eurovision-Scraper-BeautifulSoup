import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from bs4 import BeautifulSoup

user_agent = 'EurovisionScraper/1.0 (student project; python-requests)'
results = {}
url = "https://en.wikipedia.org/wiki/Eurovision_Song_Contest_"
for num in range(10):
    url = "https://en.wikipedia.org/wiki/Eurovision_Song_Contest_"
    currentYear = 2016+num
    if currentYear == 2020 or currentYear == 2022:
        continue
    url += str(currentYear)
    my_headers = {'User-Agent': user_agent}
    response = requests.get(url, headers=my_headers)
    response.raise_for_status()
    data = response.content
    soup = BeautifulSoup(data, "html.parser")
    if 2021 < currentYear:
        table = soup.findAll('table', {'class':"wikitable plainrowheaders", 'style':"text-align: center; font-size: 85%;"})[0]
    else:
        table = soup.findAll('table', {'class': "wikitable plainrowheaders", 'style': "text-align:center; font-size:85%;"})[4]
    countries = table.findAll('tr')[3:]
    israel = []
    for country in countries:
        if "Israel" in country.get_text().strip():
            cha = country.get_text().strip().replace('\n', ' ')
            nch = ''
            for i in range(len(cha)):
                if (cha[i] != ' '):
                    nch += cha[i]
                if (cha[i] == ' ' and nch != '') or i == len(cha)-1:
                    israel.append(nch)
                    nch = ''
    if currentYear == 2017:
        israel = [int(israel[2]), int(israel[3]), int(israel[4])]
    else:
        israel = [int(israel[1]), int(israel[2]), int(israel[3])]
    results[url[-4:]]=israel

    split_tables = [t for t in soup.findAll('table', class_="collapsible")
                    if t.find('caption') and "Split results" in t.find('caption').get_text()]
    table = split_tables[-1]
    countries = table.findAll('tr')[2:]
    israel = {}
    index = 0
    for country in countries:
        israel[index] = []
        if "Israel" in country.get_text().strip():
            cha = country.get_text().strip().replace('\n', ' ')
            nch = ''
            for i in range(len(cha)):
                if (cha[i] != ' '):
                    nch += cha[i]
                if (cha[i] == ' ' and nch != '') or i == len(cha) - 1:
                    israel[index].append(nch)
                    nch = ''
        index += 1
    score = ''
    for k, v in israel.items():
        if v != [] and 'Israel' in v[1]:
            score = v[0]
            results[url[-4:]].append(int(score))

with pd.ExcelWriter("Eurovision_Results_by_year_2016_2025.xlsx", engine="openpyxl") as writer:
    for year, data in results.items():
        df = pd.DataFrame([{
            "Eurovision Year": year,
            "Total Score": data[0],
            "Jury Score": data[1],
            "Televoting Score": data[2],
            "Place": data[3]
        }])
        df.to_excel(writer, sheet_name=year, index=False)

df = pd.DataFrame.from_dict(results, orient="index", columns=["Total Score", "Jury Score", "Televoting Score", "Place"])
df.index.name = "Eurovision Year"
df.reset_index(inplace=True)
df["Eurovision Year"] = df["Eurovision Year"].astype(int)
df["Gap"] = df["Jury Score"] - df["Televoting Score"]
plt.figure(figsize=(10, 6))
plt.plot(df["Eurovision Year"], df["Gap"], color="red", marker="o", label="Gap (Jury - Televote)")
plt.axhline(0, color="gray", linestyle="--")
plt.title("Gap between Jury and Televoting Scores (Israel 2016-2025)")
plt.xlabel("Year")
plt.ylabel("Gap (Jury - Televote)")
plt.xticks(list(range(2016, 2026)))
plt.grid(True)
plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=1)
plt.tight_layout()
plt.savefig("Jury_Televote_Gap-Graph_1.png")
plt.close()


df["Jury Ratio"] = df["Jury Score"] / df["Total Score"]
df["Televote Ratio"] = df["Televoting Score"] / df["Total Score"]
df["Main Impact"] = df.apply(lambda row: "Televoting" if row["Televote Ratio"] > row["Jury Ratio"] else "Jury", axis=1)
colors = df["Main Impact"].map({"Televoting": "green", "Jury": "blue"})
plt.figure(figsize=(10, 6))
plt.bar(df["Eurovision Year"], df["Televote Ratio"] - df["Jury Ratio"], color=colors)
plt.axhline(0, color="black", linestyle="--")
plt.title("Main Influence on Israel's Final Score (Televoting vs Jury)")
plt.xlabel("Year")
plt.ylabel("Televote - Jury Ratio")
plt.xticks(list(range(2016, 2026)))
plt.grid(axis="y", linestyle=":", alpha=0.7)
jury_patch = mpatches.Patch(color="blue", label="Jury")
televote_patch = mpatches.Patch(color="green", label="Televoting")
plt.legend(handles=[televote_patch, jury_patch], loc="lower center", bbox_to_anchor=(0.5, -0.3), ncol=2)
plt.tight_layout()
plt.savefig("Televoting_vs_Jury_Final_Score-Graph_2.png")
plt.close()


plt.figure(figsize=(10, 6))
plt.plot(df["Eurovision Year"], df["Place"], marker="o", linestyle="-", color="purple", label="Final Position")
plt.title("Israel's Final Eurovision Position (2016-2025)")
plt.xlabel("Year")
plt.ylabel("Final Place")
plt.gca().invert_yaxis()
plt.xticks(list(range(2016, 2026)))
plt.grid(True, linestyle=":", alpha=0.7)
plt.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=1)
plt.tight_layout()
plt.savefig("Israel_Final_Position-Graph_3.png")
plt.close()

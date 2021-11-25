import pandas as pd
import matplotlib.pyplot as plt

codecounts_week = pd.read_csv(
    filepath_or_buffer = "output/codecounts_week.csv"
)
codecounts_total = codecounts_week.sum()

#################################### plots 1 ###################################
def plotstyle(axesrow, axescol, title):
    axs[axesrow,axescol].set_ylabel('Count per week')
    axs[axesrow,axescol].xaxis.set_tick_params(labelrotation=70)
    #axs[0,0].set_ylim(bottom=0) # might remove this in future depending on count fluctuation
    axs[axesrow,axescol].grid(axis='y')
    axs[axesrow,axescol].legend()
    axs[axesrow,axescol].set_title(title, loc='left', y=1)
    axs[axesrow,axescol].tick_params(labelbottom=True)
    axs[axesrow,axescol].spines["left"].set_visible(False)
    axs[axesrow,axescol].spines["right"].set_visible(False)
    axs[axesrow,axescol].spines["top"].set_visible(False)
    

fig, axs = plt.subplots(2, 2, figsize=(15,12), sharey=False,  sharex=True)

probable = [col for col in codecounts_week if col.startswith('probable')]
for v in probable:
    axs[0,0].plot(
        codecounts_week.index, 
        codecounts_week[v], 
        marker='o', 
        markersize=2, 
        label=f"""Code for probable case, N={codecounts_total[v]}""",
        )

plotstyle(0,0, "Primary Care Probable COVID-19\n");

suspected = [col for col in codecounts_week if col.startswith('suspected')]
for v in probable:    
    axs[0,1].plot(
        codecounts_week.index, 
        codecounts_week[suspected], 
        marker='o', 
        markersize=2, 
        label=f"""Code for suspected, N={codecounts_total[suspected]}""",
        )
plotstyle(0,1, "Primary Care Suspected COVID-19\n");


axs[1,0].plot(
    codecounts_week.index, 
    codecounts_week["sgss_positive_test"], 
    marker='o', 
    markersize=2, 
    label=f"""SGSS positive test, N={codecounts_total["sgss_positive_test"]}""",
    )
plotstyle(1,0, "SGSS tests\n");

axs[1,1].plot(
    codecounts_week.index, 
    codecounts_week["antigen_negative"], 
    marker='o', 
    markersize=2, 
    label=f"""Code for negative antigen test, N={codecounts_total["antigen_negative"]}""",
    )
axs[1,1].legend()
plotstyle(1,1, "Primary Care antigen negative\n");

plt.tight_layout()
plt.savefig("output/plots.svg")
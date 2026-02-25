import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde

val_indices_tt_domaine = [907,907,894,848,821,747,708,687,670,654,651,649,661,683,743,796,935]

val_vorti_tt_domaine = [1,10,15,25,30,40,45,50,55,60,62.5,65,67.5,70,80,90,100]


val_vorti_mdr = [0,10,15,20,25,35,45,55,65,67.5,70,72.5,75,80,85,95,100]

val_indice_mdr = [801,801,810,814,835,831,792,783,771,767,757,762,765,771,791,796,796]

plt.plot(val_vorti_tt_domaine, val_indices_tt_domaine, label = 'Tout domaine')
plt.plot(val_vorti_mdr, val_indice_mdr, label = 'Domaine MDR')
plt.title("Différence d'intensité cyclogénèse (ALADIN - IBTRACS) selon seuil vorticité sur ALADIN")
plt.xlabel('seuil vorticité')
plt.ylabel('\Delta intensité cyclogénèse')
plt.legend()
#plt.show()

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from numpy import random
from scipy import stats

Nsample = 5000
xx = random.normal(size=Nsample)
yy = random.normal(size=Nsample)

kde = stats.gaussian_kde([xx,yy])
zz = kde([xx,yy])
zz.min(),zz.max()

cc = cm.jet((zz-zz.min())/(zz.max()-zz.min()))
cc.min(),cc.max()

fig = plt.figure(figsize=(4.3,4))
ax = plt.subplot(1,1,1)
ax.scatter(xx,yy,marker='o',facecolors=cc,s=1)
ax.set_aspect('equal','datalim')


plt.colorbar()

plt.show()
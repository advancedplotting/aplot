from matplotlib import pyplot as plt
import numpy as np

data = np.random.random((10,10))

plt.pcolormesh(data**4)
plt.show()

np.savetxt('tiles.txt', data)


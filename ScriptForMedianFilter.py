import numpy as np
import matplotlib.pyplot as plt
import cv2


medianFilteredData = cv2.medianBlur(data,5)
plt.imshow(medianFilteredData)
plt.title('medianFilteredData')
plt.colorbar()
plt.show(block = True)

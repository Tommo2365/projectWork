
import numpy as np
import matplotlib.pyplot as plt


    profiles = np.array([])
    allProfiles = []
    count = 0
    indices =  [89, 169, 249]
    for index in indices:
        profiles = csvData[index,:]
        count = count +1 
        allProfiles.append(profiles)
    allProfiles = np.array(allProfiles)
        


    plt.plot(allProfiles[0,:])
    plt.plot(allProfiles[1,:])
    plt.plot(allProfiles[2,:])
    plt.title('profile')
    #plt.colorbar()
    plt.xlabel("distance along profile")
    plt.ylabel("Temp degrees")
    plt.legend(["line " + str(indices[0]), "line " + str(indices[1]), "line " + str(indices[2])])
    plt.show(block = True)


    
import os


def GetFileNames(folderName, fileType):
    
    print('Scanning Dir:    ' + folderName)

    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(folderName):
        for file in f:
            if fileType in file:
                files.append(os.path.join(r, file))

    #for f in files:
        #print(f)
        
    
    return files

    
    

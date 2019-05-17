import sys
from Core.Scaners.Other import SaveClasses, SaveSpecs, SaveTalants, addWoWToken, addUser, addZeroLastItem, addClient

if __name__=="__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'all':
            if len(sys.argv) > 5:
                addUser(sys.argv[2], sys.argv[3])
                SaveClasses()
                SaveSpecs()
                SaveTalants()
                addWoWToken()
                addClient(sys.argv[4], sys.argv[5])
                addZeroLastItem()
                print("Added user, cls, specs, talants, zero, client,wowt.")
            else:
                print("Expected 5 args.. (user name; pass; client_id, client_secret")
        elif sys.argv[1] == 'wt':
            addWoWToken()
            print("Added wowtoken")
        elif sys.argv[1] == 'zero':
            addZeroLastItem()
            print("Added ZeroLastItem")
        elif sys.argv[1] == 'talents':
            SaveClasses()
            SaveSpecs()
            SaveTalants()
            print("Added cls, specs, talents")
        elif sys.argv[1] == 'client':
            addClient(sys.argv[2], sys.argv[3])
            print("Added client")
        elif sys.argv[1] == 'user':
            addUser(sys.argv[2], sys.argv[3])
            print("Added user")
        else:
            print("Unknown arg..")
    else:
        print("Nothing..")




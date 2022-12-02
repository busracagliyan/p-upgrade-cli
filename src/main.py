import argparse
import subprocess
import pandas as pd
import apt
from Check import Check
from Package import Package

Package = Package()
check = Check()

def main():
    parser = argparse.ArgumentParser(prog="pardus-upgrade-cli")

    parser.add_argument("-c", "--check", action="store_const", const="check",
                    dest="check", help="control upgradable packages or version")
    parser.add_argument("-u", "--upgrade", action="store_const",
                    const="upgrade", dest="upgrade", help="upgrade all packages")
    parser.add_argument("-v", "--version-upgrade", action="store_const",
                    const="version_upgrade", dest="version_upgrade", help="upgrade version")
    parser.add_argument("-f", "--fix", action="store_const", const="fix",
                    dest="fix", help="tries to fix if any broken packages")
    parser.add_argument("-y", "--yes", action="store_true", dest="yes", help="")

    args = parser.parse_args()

    if args.check:
        print("checking...")

        try:
            cache = apt.Cache()
            cache.open()
            cache.update()    
        except Exception as e:
            print(str(e))
            print("error!")
            subprocess.getoutput("apt update")
        
        upgradable_packages()

        check.check_version()

    if args.upgrade:
        print("upgrading...")
        upgradable_packages()
        subprocess.getoutput("apt update")

        #print("devam edebilmek için y or yes yazın")
        if args.yes:
            subprocess.getoutput("apt full-upgrade")
        else:
            print("iptal")

    if args.version_upgrade:
        print("version-upgrading....")
        
        if args.yes:
            # sourceslist güncellenecek
            subprocess.getoutput("apt update")
            subprocess.getoutput("apt full-upgrade")
        else:
            print("iptal")

    if args.fix:
        print("fixing....")

def upgradable_packages():
    download_size, space_size = Package.required_size()
    upgradable, newly_installed, removed, kept = Package.upgradable_package_check()
    
    print(("Need to get ") +str(download_size) + (" of archives.") +
                (" After this operation, ") + str(space_size) + (" of additional disk space will be used."))
    print(str(len(upgradable)) +  (" upgraded, ") + str(len(newly_installed))+ (" newly installed, ")
         + str(len(removed)) + (" to remove, ") + str(len(kept)) + (" not upgraded"))

    show_table("upgradable",upgradable)
    show_table("newly installed",newly_installed)
    show_table("removed",removed)
    show_table("kept",kept)

def show_table(name,package):
    if package == None or package ==[]:
        #print(name + " packages is none")
        pass
    else:
        new_version = []
        for pkg in package:
            new_version.append(Package.version(pkg))

        old_version = []
        for pkg in package:
            old_version.append(Package.installedVersion(pkg))        

        df1 = pd.DataFrame(new_version, columns=['new version'])
        df2 = pd.DataFrame(old_version, columns=['old version'])
        df3 = pd.DataFrame(package, columns=[name])

        df = pd.concat([df3,df2,df1],axis=1)
        print("\n************")
        print(df.to_string())
        print("\n")

if __name__ == "__main__":
    main()

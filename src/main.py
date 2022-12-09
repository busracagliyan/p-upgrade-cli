import argparse
import subprocess
from time import strftime
import pandas as pd
import apt
from Check import Check
from Package import Package

Package = Package()
check = Check()

def main():
    parser = argparse.ArgumentParser(prog="pardus-upgrade-cli")
    subparsers = parser.add_subparsers(dest='command')

    parser.add_argument("-c", "--check", action="store_const", const="check",
                    dest="check", help="control upgradable packages or version")
    parser.add_argument("-u", "--upgrade", action="store_const",
                    const="upgrade", dest="upgrade", help="upgrade all packages")
    parser.add_argument("-v", "--version-upgrade", action="store_const",
                    const="version_upgrade", dest="version_upgrade", help="upgrade version")
    parser.add_argument("-f", "--fix", action="store_const", const="fix",
                    dest="fix", help="tries to fix if any broken packages")
    parser.add_argument("-y", "--yes", action="store_true", dest="yes", help="")

    parser_yes = subparsers.add_parser("-y", help="")
    parser_yes.add_argument("-y", "--yes", action="store_true", dest="yes", help="")

    args = parser.parse_args()

    download_size, space_size = Package.required_size()
    upgradable, newly_installed, removed, kept = Package.upgradable_package_check()

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
        
        upgradable_packages(upgradable, newly_installed, removed, kept)
        print_size(download_size, space_size,upgradable, newly_installed, removed, kept )
        check.check_version()

    if args.upgrade:
        print("upgrading...")
        subprocess.getoutput("apt update")
        upgradable_packages(upgradable, newly_installed, removed, kept)
        print_size(download_size, space_size,upgradable, newly_installed, removed, kept )
        print("devam edebilmek için y or yes yazın", args.yes)
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

def upgradable_packages(upgradable, newly_installed, removed, kept ):
    print(show_table2("upgradable",packages(upgradable)))
    # show_table("newly installed",newly_installed)
    # show_table("removed",packages(removed))
    show_table("kept",packages(kept))

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

def show_table2(name,pkgs):
    text = list()
    text.append('Check Time %s' %strftime('%m/%d/%Y %H:%M:%S'))

    if not pkgs:
        text.append('No avaible updates on this machine.')
    else:
        pkg_name = name + ' packages list'
        text.append(pkg_name)
        text.append('%d packages can be updated.' % len(pkgs))
        text.append('-'*120)
        text.append('Package Name'.ljust(40) + 
        'Current Version'.ljust(40) +
        'Latest Version'.ljust(40))
        text.append('-'*120)

        for pkg in pkgs:
            text.append('{:<40}|{:<40}|{:<40}'.format(
                pkg.get('name'),
                pkg.get('current_version'),
                pkg.get('candidate_version')
            ))
        text.append('='*120)
        return '\n'.join(text)

def packages(pkgs):
    dict = []
    for pkg in pkgs:
        record = {"name":pkg,
        "current_version": Package.installedVersion(pkg),
                  "candidate_version": Package.version(pkg)}

        dict.append(record)
    
    return dict        

def print_size(download_size, space_size,upgradable, newly_installed, removed, kept ):
    print(("Need to get ") +str(download_size) + (" of archives.") +
                (" After this operation, ") + str(space_size) + (" of additional disk space will be used."))
    print(str(len(upgradable)) +  (" upgraded, ") + str(len(newly_installed))+ (" newly installed, ")
         + str(len(removed)) + (" to remove, ") + str(len(kept)) + (" not upgraded"))
    print("\n")

if __name__ == "__main__":
    main()

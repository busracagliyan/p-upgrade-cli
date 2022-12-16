import argparse
import os
import subprocess
from time import strftime
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
    parser.add_argument("-y", "--yes", action="store_true",
                        dest="yes", help="allows continuing the process")

    args = parser.parse_args()

    download_size, space_size = Package.required_size()
    upgradable, newly_installed, removed, kept = Package.upgradable_package_check()

    if args.check:
        print("Checking...")

        try:
            cache = apt.Cache()
            cache.open()
            cache.update()
        except Exception as e:
            print(str(e))
            print("error!")
            subprocess.getoutput("apt update")

        upgradable_packages(upgradable, newly_installed, removed, kept)
        print_size(download_size, space_size, upgradable,
                   newly_installed, removed, kept)
        check.check_version()

    if args.upgrade:
        print("Checking for upgrade...")
        subprocess.getoutput("apt update")

        upgradable_packages(upgradable, newly_installed, removed, kept)
        print_size(download_size, space_size, upgradable,newly_installed, removed, kept)

        if download_size == '0.0 KB' and space_size=='0.0 KB':
            print("Your system is up to date")
        else:
            if args.yes == False:
                args.yes = input("Do you want to continue? [y/n] ")

                if args.yes == "y" or args.yes == "Y":
                    print("Starting upgrade")
                    subprocess.getoutput("apt update")
                    print("continue...")
                    subprocess.call(["apt", "full-upgrade", "-yq", "-o", "APT::Status-Fd=2"],
                                    env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'})
                    print("Done!")
                elif args.yes == "n" or args.yes == "N":
                    print("The process has been canceled.")
                else:
                    print("Invalid argument.")
            else:
                print("Starting upgrade")
                subprocess.getoutput("apt update")
                print("continue...")
                subprocess.call(["apt", "full-upgrade", "-yq", "-o", "APT::Status-Fd=2"],
                                env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'})
                print("Done!")

    if args.version_upgrade:
        print("Checking for version upgrade....")
        check_v = check.check_version()

        if check_v == True:
            # print_size(download_size, space_size, upgradable, newly_installed, removed, kept)

            if args.yes == False:
                args.yes = input("Do you want to continue? [y/n] ")

                if args.yes == "y" or args.yes == "Y":
                    print("Starting version upgrade")
                    check.checkcorrectsourceslist()
                    subprocess.getoutput("apt update")
                    print("continue...")
                    subprocess.call(["apt", "full-upgrade", "-yq", "-o", "APT::Status-Fd=2"],
                                    env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'})
                    subprocess.call(["/sbin/reboot"])
                    print("Done!")
                elif args.yes == "n" or args.yes == "N":
                    print("The process has been canceled.")
                else:
                    print("Invalid argument.")
            else:
                print("Starting version upgrade")
                check.checkcorrectsourceslist()
                subprocess.getoutput("apt update")
                print("continue...")
                subprocess.call(["apt", "full-upgrade", "-yq", "-o", "APT::Status-Fd=2"],
                                env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive'})
                print("Done!")

    if args.fix:
        print("fixing....")


def upgradable_packages(upgradable, newly_installed, removed, kept):
    show_table("Upgradable", packages(upgradable))
    show_table("Newly installed", packages(newly_installed))
    show_table("Removed", packages(removed))
    show_table("Kept", packages(kept))


def show_table(name, pkgs):
    text = list()

    if not pkgs:
        text.append('No avaible updates on this machine.')
    else:
        pkg_name = '\n'+name + ' Packages List'
        text.append(pkg_name)
        text.append('%d packages can be updated.' % len(pkgs))
        text.append('-'*120)
        text.append('Package Name'.ljust(40) +
                    '|\tCurrent Version'.ljust(40) +
                    '\t|\tLatest Version'.ljust(40))
        text.append('-'*120)

        for pkg in pkgs:
            text.append('{:<40}|\t{:<40}|\t{:<40}'.format(
                pkg.get('name'),
                pkg.get('current_version'),
                pkg.get('candidate_version')
            ))
        text.append('='*120)
        print('\n'.join(text))


def packages(pkgs):
    dict = []
    for pkg in pkgs:
        record = {"name": pkg,
                  "current_version": Package.installedVersion(pkg),
                  "candidate_version": Package.version(pkg)}

        dict.append(record)

    return dict


def print_size(download_size, space_size, upgradable, newly_installed, removed, kept):
    print('\nCheck Time %s' % strftime('%m/%d/%Y %H:%M:%S'))
    print(("\nNeed to get ") + str(download_size) + (" of archives.") +
          (" After this operation, ") + str(space_size) + (" of additional disk space will be used."))
    print(str(len(upgradable)) + (" upgraded, ") + str(len(newly_installed)) + (" newly installed, ")
          + str(len(removed)) + (" to remove, ") + str(len(kept)) + (" not upgraded"))
    print("\n")


if __name__ == "__main__":
    main()

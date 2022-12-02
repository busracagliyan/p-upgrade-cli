import apt, apt_pkg

class Package(object):
    def __init__(self):
        #self.updatecache()
        pass

    def updatecache(self):
        try:
            self.cache = apt.Cache()
            self.cache.open()
        except:
            return False
        if self.cache.broken_count > 0:
            return False
        return True

    def beauty_size(self, size):
        if type(size) is int:
            size = size / 1000
            if size > 1000000:
                size = "{:.1f} GB".format(float(size / 1000000))
            elif size > 1000:
                size = "{:.1f} MB".format(float(size / 1000))
            else:
                size = "{:.1f} KB".format(float(size))
            return size
        return "size not found"

    def broken_packages(self):
        self.cache.clear()
        broken = []
        try:
            for pkg in self.cache:
                if self.cache[pkg.name].is_now_broken:
                    broken.append(pkg.name)
                elif self.cache[pkg.name].is_inst_broken:
                    broken.append(pkg.name)
        except Exception as e:
            print("Broken Package Error: {}".format(e))  
        
        if broken == []:
            return None
        else:
            return broken

    def upgradable_package_check(self):
        self.updatecache()
        self.cache.upgrade(True)

        changes = self.cache.get_changes()

        upgradable = []
        kept_packages = []
        new_packages = []
        removed_packages = []

        try:
            for pkg in self.cache:
                if self.cache[pkg.name].is_upgradable:
                    upgradable.append(pkg.name)

            for pkg in changes:
                if pkg.is_installed:
                    if pkg.marked_delete:
                        removed_packages.append(pkg.name)
                elif pkg.marked_install:
                    new_packages.append(pkg.name)

            if self.cache.keep_count>0:
                upgradable_cache_packages = [pkg.name for pkg in self.cache if pkg.is_upgradable]
                upgradable_changes_packages = [pkg.name for pkg in changes if pkg.is_upgradable]
                kept_packages = list(set(upgradable_cache_packages).difference(set(upgradable_changes_packages)))

        except Exception as e:
            print("Upgradable Package Error: {}".format(e))

        return upgradable,new_packages,removed_packages,kept_packages

    def required_size(self):
        self.updatecache()
        self.cache.upgrade(True)
        download_size = self.cache.required_download
        required_space = self.cache.required_space

        download_size = self.beauty_size(download_size)
        required_space = self.beauty_size(required_space)

        return download_size,required_space
    
    def version(self, packagename):
        package = self.cache[packagename]
        try:
            version = package.candidate.version
        except:
            try:
                version = package.versions[0].version
            except:
                version = "not found"
        return version
    
    def installedVersion(self, packagename):
        try:
            package = self.cache[packagename]
        except:
            return None
        try:
            version = package.installed.version
        except:
            version = None
        return version

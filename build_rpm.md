---
description: Build Fedora RPM Package
---

1. **Install Build Tools** (if not present):
   ```bash
   sudo dnf install rpm-build rpmdevtools
   ```

2. **Setup RPM Build Tree**:
   ```bash
   rpmdev-setuptree
   ```

3. **Prepare Source Tarball**:
   We have provided a helper script to automate creating the correctly structured tarball and moving it to the RPM build directory.
   
   ```bash
   bash create_tarball.sh
   # This will create src/see-0.1.0.tar.gz and copy it to ~/rpmbuild/SOURCES/
   ```



5. **Build the RPM**:
   ```bash
   rpmbuild -ba ~/rpmbuild/SPECS/see.spec
   ```

6. **Verify and Install**:
   The built RPMs will be in `~/rpmbuild/RPMS/noarch/`.
   
   ```bash
   # Install locally to test
   sudo dnf install ~/rpmbuild/RPMS/noarch/see-0.1.0-1*.noarch.rpm
   ```

7. **Verify Shell Integration**:
   Open a **new terminal**. The `see` command should work immediately, and `type see` should return `see is a function`.

# TODO

## Content

* Build
  * Convert from `preseed.cfg` to [Subiquity](https://github.com/CanonicalLtd/subiquity)
* Provisioning
  * Ansible Modules (Initial Implementation - Rough)
  * Clean Up (Remove Ansible etc.)
  * Minimise Box (Remove uneeded components)
* Post-Processing
  * Vagrant Box Versioning

## Build Process
* Determine Build Tooling (Chicken and Egg Problem!)
* Pre-commit
  * Validate Packer
* Shell Script Lint
  * Use Docker Container (Chicken and Egg Problem!)
* Vagrant Testing
  * Serverspec/InSpec
  * CIS Ubuntu Server Benchmark
  
### Build Minimal

* Packer
  * Minimal Version
* Virtualbox
  * Minimal Version
  * Supported Versions
  
Circle CI or Concourse
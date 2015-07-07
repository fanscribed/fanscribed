# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

    config.ssh.forward_agent = true

    config.vm.box = "ubuntu/trusty64"

    config.vm.hostname = "fanscribed-dev"

    config.vm.network "private_network", type: "dhcp"

    config.vm.synced_folder "salt/roots", "/srv"
    config.vm.synced_folder "..", "/vagrant"

    config.vm.provision 'shell', path: 'vagrant/set-apt-mirrors.sh'
    config.vm.provision 'shell', path: 'vagrant/install-upgrades.sh'

    config.vm.provision :salt do |salt|
        salt.verbose = true
        salt.minion_config = "salt/minion"
        salt.run_highstate = true
    end

    config.vm.provider "vmware_fusion" do |v|
        v.vmx["memsize"] = "2048"
        v.vmx["numvcpus"] = "2"
    end

end

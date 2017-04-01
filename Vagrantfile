Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/xenial64"

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "1024"
  end
  config.vm.network "private_network", type: "dhcp"
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.synced_folder ".", "/home/vagrant/audiobook", type: "nfs"
  config.vm.provision :shell,
    :path => "etc/install/install.sh",
    :args => ["audiobook", "audiobooks", "myprojectuser", "password"]
end
import imp, json, requests, sys
from packerlicious import builder, post_processor, provisioner, \
        Ref, Template, UserVar
from packerpy import PackerExecutable

boot_command_prefix = \
    UserVar("boot_command_prefix","<esc><esc><enter><wait>")
build_cpus = UserVar("build_cpus","2")
cpus = UserVar("cpus","2") 
disk_size = UserVar("disk_size","81920")
headless = UserVar("headless","false")
hostname = UserVar("hostname","vagrant")
#iso_checksum_url = \
#    UserVar("iso_checksum_url", \
#        "http://archive.ubuntu.com/ubuntu/dists/bionic-updates/main/installer-amd64/current/images/SHA256SUMS")
iso_checksum_url = \
    UserVar("iso_checksum_url", \
        "http://cdimage.ubuntu.com/releases/18.04.4/release/SHA256SUMS")
#iso_url = \
#    UserVar("iso_url", \
#        "http://archive.ubuntu.com/ubuntu/dists/bionic-updates/main/installer-amd64/current/images/netboot/mini.iso")
iso_url = \
    UserVar("iso_url", \
        "./iso/ubuntu-18.04.4-server-amd64.iso")
        #"http://cdimage.ubuntu.com/releases/18.04.4/release/ubuntu-18.04.4-server-amd64.iso")
locale = UserVar("locale","en_NZ")
memory = UserVar("memory","2048")
preseed = UserVar("preseed","server.cfg")
ssh_password = UserVar("ssh_password","vagrant")
ssh_username = UserVar("ssh_username","vagrant")
time_zone = UserVar("time_zone","Pacific/Auckland")
user_uid = UserVar("user_uid","1000")
vm_name = UserVar("vm_name","ubuntu1804-server-base")

desktop_user_variables = [
	boot_command_prefix,
	build_cpus,
	cpus,
	disk_size,
	headless,
	hostname,
        iso_checksum_url,
	iso_url,
	locale,
	memory,
	UserVar("preseed","desktop.cfg"),
	ssh_password,
	ssh_username,
	time_zone,
	user_uid,
        UserVar("vm_name","ubuntu1804-desktop-base")
        ]

builders = [
	builder.VirtualboxIso(
                
		boot_command = [
			Ref(boot_command_prefix),
			"/install/vmlinuz",
                        " noapic",
                        " initrd=/install/initrd.gz",
			" debian-installer/locale=" + Ref(locale).data,
                        " debian-installer/language=en",
                        " debian-installer/country=NZ",
                        " auto",
                        " kbd-chooser/method=us",
                        " hostname=" + Ref(hostname).data,
			" grub-installer/bootdev=/dev/sda<wait>",
                        " fb=false",
                        " debconf/frontend=noninteractive",
			" keyboard-configuration/modelcode=SKIP",
                        " keyboard-configuration/layout=USA",
                        " keyboard-configuration/variant=USA",
                        " console-setup/ask_detect=false",
			" netcfg/get_domain=vm",
			" netcfg/get_hostname=" + Ref(hostname).data,
			" passwd/user-default-groups='" + Ref(ssh_username).data + " sudo'", 
			" passwd/user-fullname=" + Ref(ssh_username).data,
			" passwd/user-uid=" + Ref(user_uid).data,
			" passwd/user-password=" + Ref(ssh_password).data,
			" passwd/user-password-again=" + Ref(ssh_password).data,
			" passwd/username=" + Ref(ssh_username).data,
			" preseed/url=http://{{ .HTTPIP }}:{{ .HTTPPort }}/" +
				Ref(preseed).data,
			" time/zone=" + Ref(time_zone).data,
	        	" -- ",
			"<enter>"
		],
		boot_wait = "5s",
		cpus = Ref(build_cpus),
		disk_size = Ref(disk_size),
		guest_additions_path = "VBoxGuestAdditions_{{.Version}}.iso",
		guest_os_type = "Ubuntu_64",
		hard_drive_interface = "sata",
		headless = Ref(headless),
		http_directory = "http",
                iso_checksum_url = Ref(iso_checksum_url),
		iso_checksum_type = "sha256",
		iso_url = Ref(iso_url),
		output_directory = "builds/packer-" + Ref(vm_name).data +
			"-virtualbox-iso",
		post_shutdown_delay = "1m",
		shutdown_command = 
			"echo '" + Ref(ssh_password).data + "' | sudo -S shutdown -P now",
		ssh_username = Ref(ssh_username),
		ssh_password = Ref(ssh_password),
		ssh_timeout = "10000s",
		vboxmanage = [
			[ "modifyvm", "{{.Name}}", "--nictype1", "virtio" ],
	    	        [ "modifyvm", "{{.Name}}", "--memory", Ref(memory).data ],
			[ "modifyvm", "{{.Name}}", "--cpus", Ref(cpus).data ],
		],
		virtualbox_version_file = ".vbox_version",
		vm_name = Ref(vm_name)	
	)	
]

provisioners = [
    provisioner.Shell(
        execute_command = "echo '" + Ref(ssh_password).data + \
                "' | {{.Vars}} sudo -E -S bash '{{.Path}}'",
        expect_disconnect = "true",
        scripts = [
            "scripts/desktop.sh",
            "scripts/setup.sh",
            "scripts/ansible.sh"
        ]
    ),
    provisioner.AnsibleLocal(
        playbook_file = "shared/main.yml",
        galaxy_file = "shared/requirements.yml"
    ),
    provisioner.Shell(
        execute_command = "echo '" + Ref(ssh_password).data + \
                "' | {{.Vars}} sudo -E -S bash '{{.Path}}'",
        expect_disconnect = "true",
        scripts = [
            "scripts/clean.sh"
        ]
    ),
]

# Get Next Box Version
r = requests.get("https://app.vagrantup.com/api/v1/box/catosplace/ubuntu1804-desktop-base")
resp = json.loads(r.text)

if "current_version" not in resp:
    current_box_version = None
else:
    current_box_version = resp["current_version"]

if current_box_version is None:
    next_box_version = "1.0.0"
else:
    next_box_version = str(current_box_version["version"].split('.')[0]) + "." + \
            str(current_box_version["version"].split('.')[1]) + "." + \
            str(int(current_box_version["version"].split('.')[2]) + 1)

print("Building new catosplace/ubuntu1804-desktop-base box version " + next_box_version)
version = UserVar("version", next_box_version)

post_processors = [
    post_processor.Vagrant(
        output = "builds/ubuntu1804-desktop-base.box",
        include = [
            "info.json"
        ]
    )
]

t = Template()
t.add_variable(desktop_user_variables)
t.add_variable(version)
t.add_builder(builders)
t.add_provisioner(provisioners)
# Move to new script user artifice
#t.add_post_processor(post_processors)

# View Packer Template
print(t.to_json())

(ret, out, err) = PackerExecutable(machine_readable=False).validate(t.to_json())
print(out.decode('unicode_escape'))

(ret, out, err) = PackerExecutable(machine_readable=False).build(t.to_json())
print(out.decode('unicode_escape'))

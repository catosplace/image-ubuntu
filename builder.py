import imp, sys
from packerlicious import builder, post_processor, provisioner, \
        Ref, Template, UserVar
from packerpy import PackerExecutable

my_access_token = sys.argv[1]

access_token = UserVar("access_token",my_access_token)
boot_command_prefix = \
	UserVar("boot_command_prefix","<esc><wait><esc><wait><enter><wait>")
build_cpus = UserVar("build_cpus","2")
cpus = UserVar("cpus","2") 
disk_size = UserVar("disk_size","40960")
headless = UserVar("headless","true")
hostname = UserVar("hostname","vagrant")
iso_checksum = \
	UserVar("iso_checksum","e2ecdace33c939527cbc9e8d23576381c493b071107207d2040af72595f8990b")
iso_url = \
	UserVar("iso_url","http://cdimage.ubuntu.com/ubuntu/releases/18.04.4/release/ubuntu-18.04.4-server-amd64.iso")
locale = UserVar("locale","en_NZ")
memory = UserVar("memory","2048")
preseed = UserVar("preseed","server.cfg")
ssh_password = UserVar("ssh_password","vagrant")
ssh_username = UserVar("ssh_username","vagrant")
time_zone = UserVar("time_zone","Pacific/Auckland")
user_uid = UserVar("user_uid","1000")
version = UserVar("version","1.0.0")
vm_name = UserVar("vm_name","ubuntu1804-desktop")

desktop_user_variables = [
        access_token,
	boot_command_prefix,
	build_cpus,
	cpus,
	disk_size,
	headless,
	hostname,
	iso_checksum,
	iso_url,
	locale,
	memory,
	UserVar("preseed","desktop.cfg"),
	ssh_password,
	ssh_username,
	time_zone,
	user_uid,
        version,
        vm_name
]

builders = [
	builder.VirtualboxIso(
		boot_command = [
			Ref(boot_command_prefix),
			"/install/vmlinuz",
			" auto",
			" console-setup/ask_detect=false",
			" console-setup/modelcode=pc105",
			" debconf/frontend=noninteractive",
			" debian-installer=" + Ref(locale).data,
			" fb=false",
			" grub-installer/bootdev=/dev/sda",
			" initrd=/install/initrd.gz",
			" kbd-chooser/method=us",
			" keyboard-configuration/layout=USA",
			" keyboard-configuration/variant=USA",
			" keyboard-configuration/xkb-keymap=us",
			" locale=" + Ref(locale).data,
			" netcfg/get_domain=vm",
			" netcfg/get_hostname=" + Ref(hostname).data,
			" noapic",
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
		floppy_files = [
			"http/" + Ref(preseed).data
		],
		guest_additions_path = "VBoxGuestAdditions_{{.Version}}.iso",
		guest_os_type = "Ubuntu_64",
		hard_drive_interface = "sata",
		headless = Ref(headless),
		http_directory = "http",
		iso_checksum = Ref(iso_checksum), 
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
			[ "modifyvm", "{{.Name}}", "--cpus", Ref(cpus).data ]
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
            "scripts/ansible.sh",
            "scripts/setup.sh"
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

post_processors = [
        post_processor.Vagrant(
            output = "builds/ubuntu1804-base.box"
        ),
        post_processor.VagrantCloud(
            box_tag = "catosplace/ubuntu1804-desktop",
            access_token = Ref(access_token),
            version = Ref(version)
        )
]

t = Template()

t.add_variable(desktop_user_variables)
t.add_builder(builders)
t.add_provisioner(provisioners)
t.add_post_processor(post_processors)

#View Packer Template
#print(t.to_json())

(ret, out, err) = PackerExecutable(machine_readable=False).validate(t.to_json())
print(out.decode('unicode_escape'))

(ret, out, err) = PackerExecutable().build(t.to_json())
print(out.decode('unicode_escape'))

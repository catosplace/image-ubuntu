from packerlicious import builder, post_processor, provisioner, \
        Ref, Template, UserVar
from packerpy import PackerExecutable

from dotenv import load_dotenv
load_dotenv()

import os
token = os.environ.get("cloud_token")

cloud_token = UserVar("cloud_token", token)

user_variables = [ cloud_token ]

builders = [
    builder.Null(
        communicator = "none"
    )
]

post_processors = [
        [
            post_processor.Artifice(
                files = [
                    "builds/ubuntu1804-desktop-base.box"
                ]
            ),
            post_processor.VagrantCloud(
                box_tag = "catosplace/ubuntu1804-desktop-base",
                access_token = Ref(cloud_token),
                version = "1.0.2"
            ),
            #post_processor.Checksum(
            #    checksum_types = [ "md5", "sha1", "sha256" ]
            #),
            
        ]
]

t = Template()
t.add_variable(user_variables)
t.add_builder(builders)
t.add_post_processor(post_processors)

print(t.to_json())

(ret, out, err) = PackerExecutable(machine_readable=False).validate(t.to_json())
print(out.decode('unicode_escape'))

(ret, out, err) = PackerExecutable(machine_readable=False).build(t.to_json())
print(out.decode('unicode_escape'))

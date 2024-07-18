# Base
compartment_id = ""
namespace      = ""
project_name   = ""
region         = "" # i.e. eu-frankfurt-1

# Compute
instance_image_os      = "Canonical Ubuntu"
instance_image_version = "22.04"
instance_shape         = "VM.Standard.E4.Flex"

# Network
private_ip = "10.0.23.29"
subnets    = [
  { cidr_block = "10.0.23.0/26", name = "web" }
]
vcn_cidr = "10.0.23.0/24"

# Storage
dicom_bucket_name = "DICOM-anonymization-bucket"
txt_bucket_name   = "TXT-anonymization-bucket"

# Configuration
oci_config_dir = "" # Absolute path, i.e. /home/<username/>/.oci
ssh_key_file = "" # Absolute path. Read-only, used only for ssh connections while provisioning software.
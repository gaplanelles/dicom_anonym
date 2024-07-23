# Base
compartment_id = "ocid1.compartment.oc1..aaaaaaaaqzqibhwkc6z2q3gpryyx3c5oin5leqwu2az4ro2ynrp4ebvpihnq"
namespace      = "freudoiffjpj"
project_name   = "gumed js 7"  # Max size is 15 chars due to the limitations of DNS Label
region         = "eu-frankfurt-1" # i.e. eu-frankfurt-1

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

# Storage - Names of buckets HAVE to be unique in whole namespace
dicom_bucket_name = "DICOM-anonymization-bucket-JS"
txt_bucket_name   = "TXT-anonymization-bucket-JS"

# Configuration
oci_config_dir = "/home/jswiercz/.oci" # Absolute path, i.e. /home/<username/>/.oci
ssh_key_file = "/home/jswiercz/.oci/id_rsa" # Absolute path. Read-only, used only for ssh connections while provisioning software.
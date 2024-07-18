provider "oci" {
  config_file_profile = "DEFAULT"  # The profile name in the ~/.oci/config file
}

# Include the variable definitions
terraform {
  required_providers {
    oci = {
      source = "hashicorp/oci"
    }
  }
}

# Include the resource definitions
module "net" {
  source                 = "./net"
  project_name           = var.project_name
  sanitized_project_name = local.sanitized_project_name
  compartment_id         = var.compartment_id
  vcn_cidr               = var.vcn_cidr
  subnets                = var.subnets
}

output "subnet_ids" {
  value = module.net.subnet_ids
}

module "app" {
  source                 = "./app"
  project_name           = var.project_name
  sanitized_project_name = local.sanitized_project_name
  compartment_id         = var.compartment_id
  net_subcompartment_id  = module.net.net_subcompartment_id
  namespace              = var.namespace
  dicom_bucket_name      = var.dicom_bucket_name
  txt_bucket_name        = var.txt_bucket_name
  instance_image_os      = var.instance_image_os
  instance_image_version = var.instance_image_version
  instance_shape         = var.instance_shape
  private_ip             = var.private_ip
  subnet_id              = lookup(module.net.subnet_ids, "web").id
  oci_config_dir         = var.oci_config_dir
  ssh_key_file           = var.ssh_key_file
}

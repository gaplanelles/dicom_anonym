# Base
variable "compartment_id" {
  description = "The OCID of the parent compartment"
  type        = string
}

variable "namespace" {
  description = "Object Storage namespace"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "region" {
  description = "Name of the region"
  type        = string
}



# Compute
variable "instance_image_os" {
  description = "Image OS for the instance"
  type        = string
  default     = "Canonical Ubuntu"
}

variable "instance_image_version" {
  description = "Image version for the instance"
  type        = string
  default     = "22.04"
}

variable "instance_shape" {
  description = "Shape of the compute instance"
  type        = string
  default     = "VM.Standard3.Flex"
}



# Network
variable "private_ip" {
  description = "Private IP address for the instance"
  type        = string
  default     = "10.0.23.29"
}

variable "subnets" {
  description = "List of tuples with subnet CIDR blocks and their names"
  type        = list(object({
    cidr_block = string
    name       = string
  }))
  default = [
    { cidr_block = "10.0.23.0/26", name = "web" }
  ]
}

variable "vcn_cidr" {
  description = "CIDR block for the VCN"
  type        = string
  default     = "10.0.0.0/24"
}



# Storage
variable "dicom_bucket_name" {
  description = "Name of the bucket for DICOM anonymisation"
  type        = string
  default     = "DICOM-anonymization-bucket"
}

variable "txt_bucket_name" {
  description = "Name of the bucket for TXT anonymisation"
  type        = string
  default     = "TXT-anonymization-bucket"
}



# Configuration
variable "oci_config_dir" {
  description = "OCI configuration directory, copied to the instance."
  type        = string
  default     = "~/.oci"
}

variable "ssh_key_file" {
  description = "Private SSH key for connecting to the instance"
  type        = string
}



# Calculated variables
locals {
  sanitized_project_name = lower(replace(var.project_name, " ", "_"))
}

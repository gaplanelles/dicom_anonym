# Base
variable "compartment_id" {
  description = "The OCID of the parent compartment"
  type        = string
}

variable "namespace" {
  description = "Object Storage namespace"
  type        = string
}

variable "net_subcompartment_id" {
  type = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "sanitized_project_name" {
  type = string
}



# Compute
variable "instance_image_os" {
  description = "Image OS for the instance"
  type        = string
}

variable "instance_image_version" {
  description = "Image version for the instance"
  type        = string
}

variable "instance_shape" {
  description = "Shape of the compute instance"
  type        = string
}



# Network
variable "private_ip" {
  description = "Private IP address for the instance"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for the instance"
  type        = string
}



# Storage
variable "dicom_bucket_name" {
  description = "Name of the bucket for DICOM anonymisation"
  type        = string
}

variable "txt_bucket_name" {
  description = "Name of the bucket for TXT anonymisation"
  type        = string
}



# Configuration
variable "oci_config_dir" {
  description = "OCI configuration directory, copied to the instance."
  type        = string
}

variable "ssh_key_file" {
  description = "Private SSH key for connecting to the instance"
  type        = string
}
# Base
variable "compartment_id" {
  type = string
}

variable "project_name" {
  type = string
}

variable "sanitized_project_name" {
  type = string
}



# Dictionaries
data "oci_core_services" "list_services" {}



# Network
variable "subnets" {
  description = "List of tuples with subnet CIDR blocks and their names"
  type        = list(object({
    cidr_block = string
    name       = string
  }))
}

variable "vcn_cidr" {
  type = string
}



# Calculated variables
locals {
  dns_label = lower(replace(var.project_name, " ", ""))
  object_storage_service = [for service in data.oci_core_services.list_services.services : {
    id         = service.id
    cidr_block = service.cidr_block
  } if can(regex("(?i)object storage", service.name))][0]
  subnets_with_labels = [
    for subnet in var.subnets : {
      cidr_block  = subnet.cidr_block
      name        = subnet.name
      display_name = "${var.sanitized_project_name}_${subnet.name}"
      dns_label   = lower(replace("${var.sanitized_project_name}_${subnet.name}", "_", ""))
    }
  ]
}

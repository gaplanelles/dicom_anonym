resource "oci_core_internet_gateway" "internet_gateway" {
  compartment_id = oci_identity_compartment.net_subcompartment.id
  vcn_id         = oci_core_vcn.vcn.id
  display_name   = "${var.sanitized_project_name}_internet_gateway"
  enabled        = true
}

output "internet_gateway_id" {
  value = oci_core_internet_gateway.internet_gateway.id
}

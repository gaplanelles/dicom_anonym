resource "oci_core_vcn" "vcn" {
  compartment_id = oci_identity_compartment.net_subcompartment.id
  cidr_block     = var.vcn_cidr
  display_name   = "${var.sanitized_project_name}_vcn"
  dns_label      = "${local.dns_label}"
}

output "vcn_id" {
  value = oci_core_vcn.vcn.id
}

resource "oci_identity_compartment" "net_subcompartment" {
  name           = "${var.sanitized_project_name}_net"
  description    = "Network subcompartment for ${var.project_name}"
  compartment_id = var.compartment_id
}

output "net_subcompartment_id" {
  value = oci_identity_compartment.net_subcompartment.id
}

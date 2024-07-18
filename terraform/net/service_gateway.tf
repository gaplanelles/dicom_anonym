resource "oci_core_service_gateway" "service_gateway" {
  compartment_id = oci_identity_compartment.net_subcompartment.id
  vcn_id         = oci_core_vcn.vcn.id
  display_name   = "${var.sanitized_project_name}_service_gateway"
  services {
    service_id = local.object_storage_service.id
  }
}

output "service_gateway_id" {
  value = oci_core_service_gateway.service_gateway.id
}

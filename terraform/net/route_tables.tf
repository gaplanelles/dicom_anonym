resource "oci_core_route_table" "route_table" {
  compartment_id = oci_identity_compartment.net_subcompartment.id
  vcn_id         = oci_core_vcn.vcn.id
  display_name   = "${var.sanitized_project_name}_route_table"
  
  route_rules {
    description       = "Traffic from / to public internet"
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_internet_gateway.internet_gateway.id
  }
  
  route_rules {
    description       = "Traffic from / to Object Storage"
    destination       = local.object_storage_service.cidr_block
    destination_type  = "SERVICE_CIDR_BLOCK"
    network_entity_id = oci_core_service_gateway.service_gateway.id
  }
}

output "route_table_id" {
  value = oci_core_route_table.route_table.id
}
